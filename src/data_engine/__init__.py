"""
Data Engine — 数据引擎与管道执行器

为上层提供跨数据源的统一访问接口.
Pipe Runner 根据 Prompt 中的 data_pipes 声明,按需执行对应的数据采集管道.
"""

from __future__ import annotations

import hashlib
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
from loguru import logger

from config.settings import DATA_DIR


@dataclass
class DataBundle:
    """
    数据采集结果容器 — 承载所有管道采集到的数据.

    DataBundle 是 PipeRunner 的输出, PromptRuntime 的输入.
    通过 pipe_id 键访问各管道数据.
    """
    data: Dict[str, pd.DataFrame] = field(default_factory=dict)
    metadata: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    errors: Dict[str, str] = field(default_factory=dict)
    collected_at: datetime = field(default_factory=datetime.now)

    def get(self, pipe_id: str, default=None) -> Optional[pd.DataFrame]:
        """根据管道ID获取数据."""
        return self.data.get(pipe_id, default)

    def has(self, pipe_id: str) -> bool:
        """检查是否成功采集了指定管道数据."""
        return pipe_id in self.data and self.data[pipe_id] is not None and not self.data[pipe_id].empty

    @property
    def pipe_ids(self) -> List[str]:
        return list(self.data.keys())

    @property
    def is_empty(self) -> bool:
        return not any(df is not None and not df.empty for df in self.data.values())

    def summary(self) -> Dict:
        return {
            "pipes_total": len(self.data) + len(self.errors),
            "pipes_success": len(self.data),
            "pipes_failed": len(self.errors),
            "pipes": {
                pid: f"{len(df)} rows" if df is not None and not df.empty else "empty"
                for pid, df in self.data.items()
            },
            "errors": self.errors,
        }


class DataPipe(ABC):
    """
    单个数据管道的抽象基类.

    每种数据源对应一个 DataPipe 子类. Pipeline 注册到 DataEngine,
    由 PipeRunner 统一调度执行.
    """

    # 子类必须声明 pipe_id (唯一标识)
    pipe_id: str = ""

    @abstractmethod
    def collect(self, params: Dict) -> pd.DataFrame:
        """
        核心采集方法.

        Args:
            params: Prompt 定义中的 params 字段

        Returns:
            pd.DataFrame — 采集到的结构化数据
        """
        ...

    def validate(self, data: pd.DataFrame) -> bool:
        """校验采集到的数据是否有效."""
        if data is None or data.empty:
            return False
        return True

    def source_attribution(self) -> List[str]:
        """声明数据来源(引用追踪)."""
        return []

    def cache_key(self, params: Dict) -> str:
        """生成缓存键."""
        param_str = json.dumps(params, sort_keys=True, default=str)
        raw = f"{self.pipe_id}:{param_str}"
        return hashlib.md5(raw.encode()).hexdigest()[:12]


class PipeRunner:
    """
    管道执行器 — 将 Prompt 中的 data_pipes 声明转化为实际数据.

    特性:
    - 支持并行执行(ThreadPoolExecutor)
    - 支持缓存(避免重复采集)
    - 失败降级(单个管道失败不阻塞整体)
    - 引用追踪

    实际 Pipe 实现在 src/data_engine/pipes/ 目录.
    """

    def __init__(self, cache_enabled: bool = True, max_workers: int = 4):
        self._pipe_registry: Dict[str, Callable[..., DataPipe]] = {}
        self._cache_enabled = cache_enabled
        self._max_workers = max_workers
        self._cache_dir = DATA_DIR / "store"
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    def register(self, pipe_id: str, factory: Callable[..., DataPipe]):
        """注册一个数据管道."""
        self._pipe_registry[pipe_id] = factory
        logger.debug(f"注册 Pipe: {pipe_id}")

    def register_pipe(self, pipe_cls: type):
        """类装饰器方式注册."""
        if not pipe_cls.pipe_id:
            raise ValueError(f"DataPipe 子类必须声明 pipe_id: {pipe_cls}")
        self._pipe_registry[pipe_cls.pipe_id] = lambda **kw: pipe_cls(**kw)
        return pipe_cls

    def list_pipes(self) -> List[str]:
        """列出所有已注册的管道."""
        return sorted(self._pipe_registry.keys())

    def has_pipe(self, pipe_id: str) -> bool:
        """检查管道是否已注册."""
        return pipe_id in self._cache_dir if False else pipe_id in self._pipe_registry

    def run_single(self, pipe_id: str, params: Dict = None) -> pd.DataFrame:
        """执行单个数据管道."""
        params = params or {}
        factory = self._pipe_registry.get(pipe_id)
        if not factory:
            raise ValueError(f"未注册的 Pipe: {pipe_id}. 已注册: {list(self._pipe_registry.keys())}")

        pipe = factory()

        # 检查缓存
        if self._cache_enabled:
            cache_file = self._cache_dir / f"{pipe.cache_key(params)}.parquet"
            if cache_file.exists():
                try:
                    cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
                    if cache_age < timedelta(hours=24):
                        logger.debug(f"[{pipe_id}] 使用缓存: {cache_file.name}")
                        return pd.read_parquet(cache_file)
                except Exception:
                    pass

        # 执行采集
        try:
            data = pipe.collect(params)
            if pipe.validate(data):
                # 写入缓存
                if self._cache_enabled:
                    try:
                        cache_file = self._cache_dir / f"{pipe.cache_key(params)}.parquet"
                        data.to_parquet(cache_file)
                    except Exception:
                        pass
                return data
            else:
                logger.warning(f"[{pipe_id}] 采集数据无效(空/None)")
                return pd.DataFrame()
        except Exception as e:
            logger.warning(f"[{pipe_id}] 采集失败: {e}")
            return pd.DataFrame()

    def run(self, pipe_declarations: List[Any], parallel: bool = True) -> DataBundle:
        """
        批量执行所有声明的数据管道.

        Args:
            pipe_declarations: Prompt 中 data_pipes 声明列表(DataPipeDecl 或 dict)
            parallel: 是否并行执行

        Returns:
            DataBundle — 组装后的数据结果
        """
        bundle = DataBundle()
        tasks: List[tuple] = []

        for decl in pipe_declarations:
            if hasattr(decl, 'pipe'):
                pipe_id = decl.pipe
                params = decl.params if hasattr(decl, 'params') else {}
            elif isinstance(decl, dict):
                pipe_id = decl.get("pipe", "")
                params = decl.get("params", {})
            else:
                continue
            tasks.append((pipe_id, params))

        if not tasks:
            return bundle

        logger.info(f"[PipeRunner] 开始执行 {len(tasks)} 条数据管道...")

        if parallel and len(tasks) > 1:
            with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
                futures = {
                    executor.submit(self.run_single, pid, params): pid
                    for pid, params in tasks
                }
                for future in as_completed(futures):
                    pid = futures[future]
                    try:
                        data = future.result(timeout=120)
                        if data is not None and not data.empty:
                            bundle.data[pid] = data
                            bundle.metadata[pid] = {
                                "rows": len(data),
                                "columns": list(data.columns),
                                "collected_at": datetime.now().isoformat(),
                            }
                        else:
                            bundle.errors[pid] = "empty_result"
                    except Exception as e:
                        bundle.errors[pid] = str(e)
        else:
            for pid, params in tasks:
                try:
                    data = self.run_single(pid, params)
                    if data is not None and not data.empty:
                        bundle.data[pid] = data
                        bundle.metadata[pid] = {
                            "rows": len(data),
                            "columns": list(data.columns),
                        }
                    else:
                        bundle.errors[pid] = "empty_result"
                except Exception as e:
                    bundle.errors[pid] = str(e)

        logger.info(
            f"[PipeRunner] 执行完成: "
            f"成功 {len(bundle.data)} 条, 失败 {len(bundle.errors)} 条"
        )
        return bundle


# ── 便捷单例 ──
_default_runner: Optional[PipeRunner] = None


def get_runner() -> PipeRunner:
    """获取全局 PipeRunner 单例,自动注册所有内置管道."""
    global _default_runner
    if _default_runner is None:
        _default_runner = PipeRunner()
        # 自动注册所有内置管道
        try:
            from src.data_engine.pipes.auto_register import ensure_all_pipes_registered
            ensure_all_pipes_registered()
        except Exception as e:
            logger.warning(f"自动注册管道失败: {e}")
    return _default_runner


def register_pipe(pipe_cls: type):
    """便捷注册装饰器."""
    get_runner().register_pipe(pipe_cls)
    return pipe_cls
