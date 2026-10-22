"""
Prompt Registry — 提示词注册与匹配引擎

所有 Prompt 的发现、注册、关键词匹配与生命周期管理.
这是整个 Prompt-Driven 架构的核心入口.
"""

from __future__ import annotations

import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from loguru import logger


@dataclass
class AnalysisDimension:
    """分析维度 — 对应报告的一个章节."""
    id: str
    label_zh: str
    label_en: str
    method: str
    required_data: List[str] = field(default_factory=list)


@dataclass
class DataPipeDecl:
    """数据管道声明 — 告诉引擎需要哪些数据."""
    pipe: str
    params: Dict = field(default_factory=dict)


@dataclass
class PromptDefinition:
    """单个 Prompt 的完整定义 — 声明式配置."""
    id: str
    version: int = 1
    enabled: bool = True
    label_zh: str = ""
    label_en: str = ""
    description_zh: str = ""
    description_en: str = ""
    triggers: List[str] = field(default_factory=list)
    horizon_type: str = "future_years"
    horizon_value: int = 5
    horizon_unit: str = "years"
    region_zh: str = "全球"
    region_en: str = "Global"
    country_code: str = ""
    peers: List[str] = field(default_factory=list)
    geo_hubs: List[str] = field(default_factory=list)
    geo_focus_areas: List[str] = field(default_factory=list)
    indicators: List[str] = field(default_factory=list)
    data_pipes: List[DataPipeDecl] = field(default_factory=list)
    analysis_dimensions: List[AnalysisDimension] = field(default_factory=list)
    report_template: str = "mckinsey_tech"
    report_output_dir: str = "reports/industry"
    report_sections: List[str] = field(default_factory=list)
    schedule_cadence: str = "monthly"
    schedule_day: str = "monday"
    schedule_time: str = "08:00"
    quality_min_freshness_days: int = 30
    quality_min_sources: int = 2
    allowed_sources: List[str] = field(default_factory=list)
    country_specific_exceptions: Dict = field(default_factory=dict)
    raw: Dict = field(default_factory=dict, repr=False)
    source_path: str = ""

    @property
    def vertical(self) -> str:
        """推断所属行业赛道 — 优先匹配 ID 前缀,回退到 source_path 检测."""
        # 标准前缀映射(与 prompts 子目录对应)
        prefix_map = {
            "tech_": "tech",
            "realestate_": "realestate",
            "re_": "realestate",
            "macro_": "macro",
            "visa_": "career",
            "profession_": "career",
            "studyabroad_": "studyabroad",
            "industry_": "industry",
        }
        for prefix, vertical in prefix_map.items():
            if self.id.startswith(prefix):
                return vertical
        # 回退: 从 source_path 推断 (如 "industry/profession_country.yaml" → "industry")
        if self.source_path:
            parts = Path(self.source_path).parts
            for part in parts:
                if part in ("tech", "realestate", "career", "studyabroad", "macro", "industry"):
                    return part
        return "other"

    @property
    def filename_id(self) -> str:
        """返回用于生成文件名的 ID（剥离方向前缀避免双重前缀如 realestate_re_dubai）."""
        # 仅剥离与 vertical 对应的方向前缀（不剥离国家代码如 nz_, nl_ 等）
        strip_prefixes = [
            "industry_", "studyabroad_", "realestate_",
            "profession_", "visa_", "tech_", "macro_", "re_",
        ]
        for prefix in strip_prefixes:
            if self.id.startswith(prefix):
                return self.id[len(prefix):]
        return self.id

    @property
    def display_name(self) -> str:
        return self.label_zh or self.label_en or self.id

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "vertical": self.vertical,
            "label": {"zh": self.label_zh, "en": self.label_en},
            "region": {"zh": self.region_zh, "en": self.region_en},
            "pipes": len(self.data_pipes),
            "dimensions": len(self.analysis_dimensions),
            "triggers": self.triggers[:10],
            "schedule": f"{self.schedule_cadence} @ {self.schedule_time}",
        }


class PromptRegistry:
    """
    提示词注册表 — 核心入口.

    职责:
    1. 从 prompts/ 目录自动加载所有 YAML 定义
    2. 构建关键词倒排索引(triggers → prompt_ids)
    3. 根据用户输入的关键词解析并返回最佳匹配的 Prompt
    4. 提供按赛道(crud)筛选、健康检查等运维接口
    """

    def __init__(self, prompts_dir: Path = None):
        from config.settings import BASE_DIR
        self.prompts_dir = prompts_dir or (BASE_DIR / "prompts")
        self._registry: Dict[str, PromptDefinition] = {}
        self._trigger_index: Dict[str, List[str]] = {}
        self._load_all()

    # ── 核心接口 ──

    def resolve(self, keyword: str, vertical: str = None) -> Optional[PromptDefinition]:
        """
        根据用户输入的关键词,解析并返回最佳匹配的 Prompt.

        匹配策略:
        1. 精确匹配 trigger
        2. 子串匹配 trigger
        3. 模糊匹配(id 包含关键词)

        ★ 后处理: 若匹配到 profession_* 模板,自动填充 [[country]]/[[profession]] 占位符。
        """
        if not keyword or not isinstance(keyword, str):
            return None
        kw_lower = keyword.lower().strip()

        # 内部函数: 返回前统一做职业模板填充
        def _finalize(prompt: PromptDefinition) -> PromptDefinition:
            return self._fill_career_template_if_needed(prompt, keyword)

        # 策略1: 精确匹配 trigger
        for prompt in self._registry.values():
            for trigger in prompt.triggers:
                # 防御性类型检查: 确保 trigger 是字符串
                if not isinstance(trigger, str):
                    continue
                if trigger.lower() == kw_lower:
                    if vertical is None or prompt.vertical == vertical:
                        logger.info(f"[匹配] 精确命中: '{keyword}' -> {prompt.id}")
                        return _finalize(prompt)

        # 策略2: 子串匹配 trigger
        best_score = 0
        best_prompt = None
        for prompt in self._registry.values():
            for trigger in prompt.triggers:
                # 防御性类型检查: 确保 trigger 是字符串
                if not isinstance(trigger, str):
                    continue
                tl = trigger.lower()
                if tl in kw_lower or kw_lower in tl:
                    score = len(tl)
                    if score > best_score:
                        if vertical is None or prompt.vertical == vertical:
                            best_score = score
                            best_prompt = prompt
        if best_prompt:
            logger.info(f"[匹配] 子串命中: '{keyword}' -> {best_prompt.id}")
            return _finalize(best_prompt)

        # 策略3: 模糊匹配 id / label
        for prompt in self._registry.values():
            if vertical and prompt.vertical != vertical:
                continue
            if kw_lower in prompt.id.lower():
                logger.info(f"[匹配] ID命中: '{keyword}' -> {prompt.id}")
                return _finalize(prompt)
            if kw_lower in prompt.label_zh.lower() or kw_lower in prompt.label_en.lower():
                logger.info(f"[匹配] 标签命中: '{keyword}' -> {prompt.id}")
                return _finalize(prompt)

        logger.warning(f"[未匹配] 找不到与 '{keyword}' 相关的 Prompt")
        return None

    def resolve_multi(self, keywords: List[str], vertical: str = None) -> List[PromptDefinition]:
        """支持多关键词组合,返回多个 Prompt 的合并执行计划."""
        results = []
        seen_ids = set()
        for kw in keywords:
            prompt = self.resolve(kw, vertical=vertical)
            if prompt and prompt.id not in seen_ids:
                results.append(prompt)
                seen_ids.add(prompt.id)
        return results

    def list_all(self) -> List[PromptDefinition]:
        """列出所有已注册的 Prompt."""
        return list(self._registry.values())

    def list_enabled(self) -> List[PromptDefinition]:
        """列出所有已启用的 Prompt."""
        return [p for p in self._registry.values() if p.enabled]

    def list_by_vertical(self, vertical: str) -> List[PromptDefinition]:
        """按行业赛道筛选."""
        return [p for p in self._registry.values() if p.vertical == vertical and p.enabled]

    def get(self, prompt_id: str) -> Optional[PromptDefinition]:
        """根据 ID 直接获取."""
        return self._registry.get(prompt_id)

    def _fill_career_template_if_needed(
        self, prompt: PromptDefinition, keyword: str
    ) -> PromptDefinition:
        """
        若 Prompt 为 profession_* 模板,自动填充 [[country]]/[[profession]] 占位符。
        符合宪法第 5.4 节「职业赛道路由命名规范」。
        """
        # 判断是否为职业模板 (id 含 "profession_" 或 label 含占位符)
        if "profession_" not in prompt.id and "[[country]]" not in prompt.label_zh:
            return prompt

        try:
            from src.utils.career_naming import fill_career_prompt_template
            return fill_career_prompt_template(prompt, keyword)
        except Exception as e:
            logger.warning(f"职业模板填充失败 [{prompt.id}]: {e}, 返回原始 Prompt")
            return prompt

    def show_detail(self, prompt_id: str) -> Dict:
        """获取 Prompt 的详细信息(用于 CLI --show)."""
        p = self._registry.get(prompt_id)
        if not p:
            return {}
        return p.to_dict()

    def summary(self) -> Dict:
        """注册表摘要统计."""
        return {
            "total": len(self._registry),
            "enabled": sum(1 for p in self._registry.values() if p.enabled),
            "by_vertical": {
                "macro": len(self.list_by_vertical("macro")),
                "tech": len(self.list_by_vertical("tech")),
                "realestate": len(self.list_by_vertical("realestate")),
                "career": len(self.list_by_vertical("career")),
                "studyabroad": len(self.list_by_vertical("studyabroad")),
            },
        }

    # ── 内部实现 ──

    def _load_all(self):
        """自动发现并加载 prompts/ 目录下所有有效的 YAML 定义."""
        if not self.prompts_dir.exists():
            logger.warning(f"Prompts 目录不存在: {self.prompts_dir}")
            return

        yaml_files = sorted(self.prompts_dir.rglob("*.yaml"))
        # 跳过: schema 定义文件、下划线前缀的模板文件 (如 _template_lifecycle.yaml)、
        # 以及名称含 "template" 的参考模板文件 (如 template_generic.yaml)。
        # 这些不是可执行的 Prompt 定义,误加载会产生噪声或占位符 Prompt。
        yaml_files = [
            f for f in yaml_files
            if "schema" not in f.name.lower()
            and not f.name.startswith("_")
            and "template" not in f.name.lower()
        ]

        for path in yaml_files:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    raw = yaml.safe_load(f)
                if not raw or not isinstance(raw, dict):
                    continue
                if "id" not in raw:
                    continue
                if "schema" in raw.get("id", ""):
                    continue

                prompt = self._parse_prompt(raw, path)
                if prompt:
                    self._registry[prompt.id] = prompt
                    logger.debug(f"加载 Prompt: {prompt.id} <- {path.relative_to(self.prompts_dir)}")
            except Exception as e:
                logger.warning(f"加载 Prompt 失败 [{path.name}]: {e}")

        self._build_trigger_index()
        logger.info(f"PromptRegistry 初始化完成: 共 {len(self._registry)} 个 Prompt 定义")

    def _parse_prompt(self, raw: Dict, path: Path) -> Optional[PromptDefinition]:
        """解析单个 YAML 配置为 PromptDefinition."""
        label = raw.get("label", {})
        desc = raw.get("description", {})
        horizon = raw.get("horizon", {})
        geo = raw.get("geo", {})
        report = raw.get("report", {})
        schedule = raw.get("schedule", {})
        quality = raw.get("quality", {})
        indicators_raw = raw.get("indicators", {})

        # 解析 data_pipes
        pipes = []
        for p in raw.get("data_pipes", []):
            if isinstance(p, dict) and "pipe" in p:
                pipes.append(DataPipeDecl(pipe=p["pipe"], params=p.get("params", {})))

        # 解析 analysis_dimensions
        dims = []
        for d in raw.get("analysis_dimensions", []):
            if isinstance(d, dict):
                dims.append(AnalysisDimension(
                    id=d.get("id", ""),
                    label_zh=d.get("label_zh", ""),
                    label_en=d.get("label_en", ""),
                    method=d.get("method", ""),
                    required_data=d.get("required_data", []),
                ))

        indicators = []
        if isinstance(indicators_raw, dict):
            indicators = indicators_raw.get("primary", []) + indicators_raw.get("secondary", [])
        elif isinstance(indicators_raw, list):
            indicators = indicators_raw

        peers = geo.get("peers", [])
        hubs = geo.get("hubs", []) + geo.get("focus_areas", []) + geo.get("focus_regions", [])

        # 解析国家特定数据源例外规则
        data_source_policy = raw.get("data_source_policy", {})
        country_exceptions = data_source_policy.get("country_specific_exceptions", {})

        return PromptDefinition(
            id=raw["id"],
            version=raw.get("version", 1),
            enabled=raw.get("enabled", True),
            label_zh=label.get("zh", ""),
            label_en=label.get("en", ""),
            description_zh=desc.get("zh", ""),
            description_en=desc.get("en", ""),
            triggers=raw.get("triggers", []),
            horizon_type=horizon.get("type", "future_years"),
            horizon_value=horizon.get("value", 5),
            horizon_unit=horizon.get("unit", "years"),
            region_zh=geo.get("region_zh", "全球"),
            region_en=geo.get("region_en", "Global"),
            country_code=geo.get("country_code", ""),
            peers=peers,
            geo_hubs=hubs,
            geo_focus_areas=geo.get("focus_areas", []),
            indicators=indicators,
            data_pipes=pipes,
            analysis_dimensions=dims,
            report_template=report.get("template", "mckinsey_tech"),
            report_output_dir=report.get("output_dir", "reports/industry"),
            report_sections=report.get("format", {}).get("sections", []),
            schedule_cadence=schedule.get("cadence", "monthly"),
            schedule_day=schedule.get("day_of_week", "monday"),
            schedule_time=schedule.get("time", "08:00"),
            quality_min_freshness_days=quality.get("min_data_freshness_days", 30),
            quality_min_sources=quality.get("min_sources_per_section", 2),
            allowed_sources=data_source_policy.get("allowed_sources", []),
            country_specific_exceptions=country_exceptions,
            raw=raw,
            source_path=str(path),
        )

    def _build_trigger_index(self):
        """构建关键词倒排索引."""
        self._trigger_index.clear()
        for prompt in self._registry.values():
            for trigger in prompt.triggers:
                # 跳过非字符串类型的触发器(如模板占位符 dict)
                if not isinstance(trigger, str):
                    continue
                tl = trigger.lower()
                if tl not in self._trigger_index:
                    self._trigger_index[tl] = []
                if prompt.id not in self._trigger_index[tl]:
                    self._trigger_index[tl].append(prompt.id)


# ── 便捷单例 ──
_default_registry: Optional[PromptRegistry] = None


def get_registry() -> PromptRegistry:
    """获取全局单例 PromptRegistry."""
    global _default_registry
    if _default_registry is None:
        _default_registry = PromptRegistry()
    return _default_registry


def resolve_prompt(keyword: str, vertical: str = None) -> Optional[PromptDefinition]:
    """便捷函数:解析关键词获取 Prompt."""
    return get_registry().resolve(keyword, vertical=vertical)
