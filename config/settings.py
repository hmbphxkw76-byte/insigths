"""
config/settings.py - 全局路径配置
=====================================

Prompt-Driven 架构所需的极简目录配置。
报告输出完全由 Prompt YAML 的 output_dir 字段驱动，Renderer 按需 mkdir。
此处仅初始化核心输入/缓存目录。
"""

from pathlib import Path

# ── 核心目录 ──
BASE_DIR = Path(__file__).resolve().parent.parent
PROMPTS_DIR = BASE_DIR / "prompts"
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"

# ── 运行时数据目录 ──
PIPE_STORE_DIR = DATA_DIR / "store"

# ── 确保目录存在 ──
def ensure_directories():
    """创建核心输入/缓存目录（报告目录由 Renderer 按需创建）。"""
    for d in [DATA_DIR, PIPE_STORE_DIR, REPORTS_DIR]:
        d.mkdir(parents=True, exist_ok=True)


ensure_directories()
