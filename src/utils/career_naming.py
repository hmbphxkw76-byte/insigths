"""
职业赛道标题与文件名命名解析工具

将用户输入的中/英文关键词映射为小写英文 (country_slug, profession_slug),
符合宪法第五章第 5.4 节「职业赛道路由命名规范」:
  - 国家/地区使用小写英文前缀: dubai, japan, germany 等
  - 职业使用小写英文连字符: ai-security-engineer, it-engineer 等
  - 报告文件命名: career_{country}_{profession}_{YYYYMMDD}.html
  - 标题占位符: [[country]] / [[profession]] 自动填充
"""

from __future__ import annotations

import re
from copy import deepcopy
from typing import List, Optional, Tuple

from src.prompt_registry import PromptDefinition

# ── 国家/地区映射表 ──
# 当关键词中包含任意 key 时,返回对应的 slug
COUNTRY_KEYWORDS: List[Tuple[List[str], str]] = (
    # (匹配关键词列表, 输出slug)
    (["迪拜", "阿联酋", "uae", "dubai", "阿联酋"], "dubai"),
    (["日本", "japan", "jp"], "japan"),
    (["德国", "germany", "deutschland", "de"], "germany"),
    (["新加坡", "singapore", "sg"], "singapore"),
    (["澳洲", "澳大利亚", "australia", "au"], "australia"),
    (["新西兰", "new zealand", "nz"], "nz"),
    (["英国", "uk", "united kingdom", "britain", "gb"], "uk"),
    (["加拿大", "canada", "ca"], "canada"),
    (["美国", "us", "usa", "united states", "america"], "us"),
    (["韩国", "korea", "south korea", "kr"], "korea"),
    (["沙特", "saudi", "saudi arabia", "saudiarabia"], "saudi"),
    (["卡塔尔", "qatar", "qa"], "qatar"),
    (["法国", "france", "fr"], "france"),
    (["荷兰", "netherlands", "nl", "holland"], "netherlands"),
    (["爱尔兰", "ireland", "ie"], "ireland"),
    (["芬兰", "finland", "fi"], "finland"),
    (["马来西亚", "malaysia", "my"], "malaysia"),
    (["香港", "hong kong", "hk"], "hongkong"),
)

# ── 职业映射表 ──
PROFESSION_KEYWORDS: List[Tuple[List[str], str]] = (
    (["ai安全工程师", "ai安全", "ai security engineer", "ai security"], "ai-security-engineer"),
    (["网络安全工程师", "网络安全", "cybersecurity engineer", "cyber security"], "cybersecurity-engineer"),
    (["安全工程师", "安全", "security engineer"], "security-engineer"),
    (["人工智能工程师", "ai工程师", "ai engineer"], "ai-engineer"),
    (["it工程师", "it", "it engineer", "software developer"], "it-engineer"),
    (["软件工程师", "码农", "software engineer", "programmer", "developer"], "software-engineer"),
    (["汽车工程师", "automotive engineer", "auto engineer"], "automotive-engineer"),
    (["数据分析师", "data analyst", "数据分析"], "data-analyst"),
    (["会计师", "accountant", "cpa"], "accountant"),
    (["护士", "nurse", "护理"], "nurse"),
    (["金融", "finance", "banking", "金融分析师"], "finance"),
    (["司机", "driver", "truck driver", "卡车司机"], "driver"),
    (["石油工程师", "petroleum engineer", "石油"], "petroleum-engineer"),
    (["航空", "aviation", "飞行员", "pilot"], "aviation"),
    (["工程师", "engineer", "工程师"], "engineer"),
    (["技术岗位", "技术", "tech", "technology"], "tech-professional"),
    (["教师", "teacher", "教育", "education"], "teacher"),
    (["医生", "doctor", "medical", "physician"], "doctor"),
    (["律师", "lawyer", "legal"], "lawyer"),
)


def _match_slug(keyword: str, mapping: List[Tuple[List[str], str]]) -> Optional[str]:
    """根据关键词匹配最佳 slug (优先最长匹配)."""
    keyword_lower = keyword.lower().strip()
    best_slug: Optional[str] = None
    best_len: int = 0

    for keywords, slug in mapping:
        for kw in keywords:
            kw_lower = kw.lower().strip()
            if kw_lower in keyword_lower and len(kw_lower) > best_len:
                best_slug = slug
                best_len = len(kw_lower)

    return best_slug


def resolve_career_title(keyword: str) -> Tuple[str, str]:
    """
    将用户输入的关键词映射为 (country_slug, profession_slug).

    Args:
        keyword: 用户输入的关键词, 如 "迪拜AI安全工程师" 或 "Japan IT"

    Returns:
        (country_slug, profession_slug) 如 ("dubai", "ai-security-engineer")

    示例:
        >>> resolve_career_title("迪拜AI安全工程师")
        ('dubai', 'ai-security-engineer')
        >>> resolve_career_title("日本IT")
        ('japan', 'it-engineer')
        >>> resolve_career_title("Germany automotive engineer")
        ('germany', 'automotive-engineer')
        >>> resolve_career_title("UAE cybersecurity")
        ('dubai', 'cybersecurity-engineer')
    """
    country_slug = _match_slug(keyword, COUNTRY_KEYWORDS)
    if not country_slug:
        country_slug = "global"

    profession_slug = _match_slug(keyword, PROFESSION_KEYWORDS)
    if not profession_slug:
        profession_slug = "professional"

    return (country_slug, profession_slug)


# 常见缩写词应保持大写 (不会被 str.title() 正确处理)
_ACRONYMS = {"ai", "it", "cpa", "phd", "mba", "nz", "uk", "us", "uae", "gcc"}


def _smart_title(text: str) -> str:
    """
    智能 title-case: 常规单词首字母大写,但常见缩写保持全大写.

    >>> _smart_title("ai security engineer")
    'AI Security Engineer'
    >>> _smart_title("dubai")
    'Dubai'
    """
    words = text.replace("-", " ").split()
    result = []
    for w in words:
        wl = w.lower()
        if wl in _ACRONYMS:
            result.append(wl.upper())
        else:
            result.append(w.capitalize())
    return " ".join(result)


def build_career_display_name(
    keyword: str,
    label_template_zh: str,
    label_template_en: str,
) -> Tuple[str, str]:
    """
    用解析出的 slug 填充模板占位符,生成最终显示名称.

    Args:
        keyword: 用户输入的触发关键词
        label_template_zh: 中文模板,如 "[[country]][[profession]]人才需求与就业前景深度分析"
        label_template_en: 英文模板,如 "[[country]] [[profession]] Talent Demand & Career Outlook"

    Returns:
        (display_name_zh, display_name_en)
    """
    country_slug, profession_slug = resolve_career_title(keyword)

    # 智能首字母大写: AI/IT 等缩写保持大写
    country_display = _smart_title(country_slug)
    profession_display = _smart_title(profession_slug)

    # 中文: "Dubai AI Security Engineer 人才需求与就业前景深度分析"
    # 先替换相邻占位符避免 "DubaiAI" 粘连
    combined_placeholder = "[[country]][[profession]]"
    combined_value = f"{country_display} {profession_display}"
    display_zh = (
        label_template_zh
        .replace(combined_placeholder, combined_value)
        .replace("[[country]]", country_display)
        .replace("[[profession]]", profession_display)
    )

    # 英文: "Dubai AI Security Engineer Talent Demand & Career Outlook Deep Dive"
    display_en = (
        label_template_en
        .replace(combined_placeholder, combined_value)
        .replace("[[country]]", country_display)
        .replace("[[profession]]", profession_display)
    )

    return (display_zh, display_en)


def build_career_filename(
    keyword: str,
    date_str: str,
    ext: str = "html",
) -> str:
    """
    生成职业报告的标准文件名.

    Args:
        keyword: 用户输入关键词
        date_str: 日期字符串, 格式 "20261012"
        ext: 文件扩展名

    Returns:
        如 "career_dubai_ai_security_engineer_20261012.html"
    """
    country_slug, profession_slug = resolve_career_title(keyword)
    return f"career_{country_slug}_{profession_slug}_{date_str}.{ext}"


def fill_career_prompt_template(
    prompt: PromptDefinition,
    keyword: str,
) -> PromptDefinition:
    """
    填充职业模板 Prompt 中的 [[country]] / [[profession]] 占位符.

    返回一个深拷贝的 PromptDefinition, 其中 label/description 中的占位符被解析后的值替换.

    Args:
        prompt: 原始 PromptDefinition (如 profession_country)
        keyword: 触发关键词

    Returns:
        填充后的 PromptDefinition 深拷贝
    """
    country_slug, profession_slug = resolve_career_title(keyword)
    country_display = _smart_title(country_slug)
    profession_display = _smart_title(profession_slug)

    filled = deepcopy(prompt)

    # 存储 keyword 用于后续渲染器生成文件名
    filled._career_keyword = keyword  # type: ignore[attr-defined]

    # 先替换相邻占位符避免粘连 (如 "DubaiAI Security Engineer")
    _combined = "[[country]][[profession]]"
    _combined_val = f"{country_display} {profession_display}"

    # 填充 label
    filled.label_zh = (
        filled.label_zh
        .replace(_combined, _combined_val)
        .replace("[[country]]", country_display)
        .replace("[[profession]]", profession_display)
    )
    filled.label_en = (
        filled.label_en
        .replace(_combined, _combined_val)
        .replace("[[country]]", country_display)
        .replace("[[profession]]", profession_display)
    )

    # 填充 description
    filled.description_zh = (
        filled.description_zh
        .replace(_combined, _combined_val)
        .replace("[[country]]", country_display)
        .replace("[[profession]]", profession_display)
    )
    filled.description_en = (
        filled.description_en
        .replace(_combined, _combined_val)
        .replace("[[country]]", country_display)
        .replace("[[profession]]", profession_display)
    )

    return filled


if __name__ == "__main__":
    # 快速测试
    test_keywords = [
        "迪拜AI安全工程师",
        "日本IT",
        "德国汽车工程师",
        "UAE cybersecurity",
        "Germany automotive",
        "Singapore data analyst",
        "Australia accountant",
    ]
    for kw in test_keywords:
        c, p = resolve_career_title(kw)
        fname = build_career_filename(kw, "20261012")
        zh, en = build_career_display_name(
            kw,
            "[[country]][[profession]]人才需求与就业前景深度分析",
            "[[country]] [[profession]] Talent Demand & Career Outlook Deep Dive",
        )
        print(f"  {kw:35s} → ({c}, {p})")
        print(f"    {fname}")
        print(f"    {zh}")
        print(f"    {en}")
