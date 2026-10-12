"""
来源链接解析工具 — 将来源文本解析为可点击链接

规则:
  1. 如果来源字符串内嵌 URL (含 https:// 或 http://),直接提取并使用
  2. 如果不含 URL,查询内置 URL 映射表 (SOURCE_URL_MAP)
  3. 映射表中也找不到时,保持纯文本格式(不添加链接)

这与宪法框架第五章第5.3节「来源引用规范」对齐:
  每份报告中的来源必须可直接点击打开对应网页,方便验证信息真实性,减少幻觉.
"""

from __future__ import annotations

import re
from typing import List, Optional, Tuple

# ── 权威来源 URL 映射表 ──
# 当来源字符串不含内嵌 URL 时,根据来源名称关键词匹配最佳 URL
# 格式: {来源机构关键词: (显示名称, 官方URL)}

SOURCE_URL_MAP: List[Tuple[str, str, str]] = [
    # (匹配关键词, 显示名称, URL)
    # ── 市场研究与咨询 ──
    ("Gartner", "Gartner", "https://www.gartner.com/en"),
    ("IDC", "IDC", "https://www.idc.com"),
    ("Frost & Sullivan", "Frost & Sullivan", "https://www.frost.com"),
    ("Frost & Sul", "Frost & Sullivan", "https://www.frost.com"),
    ("Forrester", "Forrester", "https://www.forrester.com"),
    ("McKinsey Global", "McKinsey Global Institute", "https://www.mckinsey.com/mgi"),
    ("McKinsey", "McKinsey & Company", "https://www.mckinsey.com"),
    ("IMD World", "IMD World Competitiveness Center", "https://www.imd.org/wcc"),
    ("World Economic Forum", "World Economic Forum", "https://www.weforum.org"),
    ("EIU", "Economist Intelligence Unit", "https://www.eiu.com"),
    ("Deloitte ME", "Deloitte Middle East", "https://www.deloitte.com/xd/en/about/offices/middle-east.html"),
    ("Deloitte", "Deloitte", "https://www.deloitte.com"),
    ("PwC GCC", "PwC Middle East", "https://www.pwc.com/m1/en.html"),
    ("PwC", "PwC", "https://www.pwc.com"),
    ("MarketsandMarkets", "MarketsandMarkets", "https://www.marketsandmarkets.com"),
    ("Cybersecurity Ventures", "Cybersecurity Ventures", "https://cybersecurityventures.com"),
    ("Chromey Tech", "Chromey Tech Research", "https://chromey.com"),

    # ── 威胁情报与安全厂商 ──
    ("Mandiant", "Mandiant (Google Cloud)", "https://www.mandiant.com"),
    ("CrowdStrike", "CrowdStrike", "https://www.crowdstrike.com"),
    ("Palo Alto", "Palo Alto Networks", "https://www.paloaltonetworks.com"),
    ("Fortinet", "Fortinet", "https://www.fortinet.com"),
    ("Check Point", "Check Point Software", "https://www.checkpoint.com"),
    ("Kaspersky", "Kaspersky", "https://www.kaspersky.com"),
    ("FireEye", "Trellix (formerly FireEye)", "https://www.trellix.com"),
    ("Trellix", "Trellix", "https://www.trellix.com"),
    ("Trend Micro", "Trend Micro", "https://www.trendmicro.com"),
    ("Cisco/Splunk", "Cisco / Splunk", "https://www.splunk.com"),
    ("Claroty", "Claroty", "https://www.claroty.com"),

    # ── 投融资数据 ──
    ("PitchBook", "PitchBook Data", "https://pitchbook.com"),
    ("Crunchbase", "Crunchbase", "https://www.crunchbase.com"),
    ("Wamda", "Wamda Capital", "https://www.wamda.com"),
    ("BECO", "BECO Capital", "https://becocapital.com"),
    ("Shorooq", "Shorooq Partners", "https://shorooq.com"),
    ("CEW Ventures", "CEW Ventures", "https://www.cewventures.com"),
    ("Sequoia", "Sequoia Capital", "https://www.sequoiacap.com"),
    ("Insight", "Insight Partners", "https://www.insightpartners.com"),
    ("Ten Eleven", "Ten Eleven Ventures", "https://www.tenelevenventures.com"),
    ("Accel", "Accel", "https://www.accel.com"),
    ("Felicis", "Felicis", "https://www.felicis.com"),
    ("ETF Partners", "ETF Partners", "https://etfpartners.com"),
    ("Thoma Bravo", "Thoma Bravo", "https://www.thomabravo.com"),
    ("Macquarie", "Macquarie Capital", "https://www.macquarie.com"),

    # ── 人才与薪资 ──
    ("Hays", "Hays", "https://www.hays.com"),
    ("Robert Half", "Robert Half", "https://www.roberthalf.com"),
    ("(ISC)²", "(ISC)²", "https://www.isc2.org"),
    ("ISACA", "ISACA", "https://www.isaca.org"),

    # ── 统计与创新指数 ──
    ("GII", "Global Innovation Index", "https://www.wipo.int/global_innovation_index"),
    ("World Bank", "World Bank", "https://data.worldbank.org"),
    ("IMF", "IMF", "https://www.imf.org"),
    ("OECD", "OECD", "https://www.oecd.org"),
    ("BLS", "U.S. Bureau of Labor Statistics", "https://www.bls.gov"),
    ("Federal Reserve", "U.S. Federal Reserve", "https://www.federalreserve.gov"),
    ("ECB", "European Central Bank", "https://www.ecb.europa.eu"),
    ("NIST", "NIST", "https://www.nist.gov"),
    ("EU Commission", "European Commission", "https://commission.europa.eu"),
    ("UK DSIT", "UK DSIT", "https://www.gov.uk/government/organisations/department-for-science-innovation-and-technology"),
    ("Bloomberg", "Bloomberg", "https://www.bloomberg.com"),
    ("Reuters", "Reuters", "https://www.reuters.com"),
    ("Financial Times", "Financial Times", "https://www.ft.com"),
    ("ArXiv", "ArXiv", "https://arxiv.org"),
    ("NeurIPS", "NeurIPS", "https://neurips.cc"),
    ("ICML", "ICML", "https://icml.cc"),
    ("ICLR", "ICLR", "https://iclr.cc"),
    ("SEC", "U.S. SEC", "https://www.sec.gov"),
    ("CAC", "CAC (China)", "http://www.cac.gov.cn"),
    ("BIS", "BIS (Bureau of Industry and Security)", "https://www.bis.gov"),
    ("METI", "METI Japan", "https://www.meti.go.jp"),
    ("White House", "White House", "https://www.whitehouse.gov"),
    ("Marsh", "Marsh", "https://www.marsh.com"),
    ("Control Risks", "Control Risks", "https://www.controlrisks.com"),
    ("Cybervisory", "Cybervisory", "https://www.cybervisory.com"),
    ("VLSI Research", "VLSI Research", "https://www.vlsiresearch.com"),
    ("Recorded Future", "Recorded Future", "https://www.recordedfuture.com"),
    ("NTT", "NTT DOCOMO Ventures", "https://www.nttdocomo-v.com"),
    ("Ernst", "EY", "https://www.ey.com"),
    ("KPMG", "KPMG", "https://kpmg.com"),

    # ── 迪拜/阿联酋官方 ──
    ("Smart Dubai", "Smart Dubai", "https://www.smartdubai.ae"),
    ("Dubai Digital Authority", "Dubai Digital Authority", "https://www.dda.gov.ae"),
    ("Dubai Statistics Center", "Dubai Statistics Center", "https://www.dsc.gov.ae"),
    ("UAE Government", "UAE Government Portal", "https://u.ae"),
    ("NCA", "NCA (UAE National Cybersecurity)", "https://nca.gov.ae"),
    ("DIFC", "DIFC (Dubai International Financial Centre)", "https://www.difc.ae"),
    ("NESA", "NESA (UAE National Electronic Security Authority)", "https://nesa.gov.ae"),
    ("CBUAE", "CBUAE (Central Bank of UAE)", "https://www.centralbank.ae"),
    ("ADNOC", "ADNOC", "https://www.adnoc.ae"),
    ("Dubai Cyber", "Dubai Cyber Security Center", "https://www.dubaicyber.ae"),

    # ── 日本官方 (JA/D 级来源) ──
    ("JAF", "JAF (日本自動車連盟)", "https://www.jaf.or.jp"),
    ("npa.go.jp", "警察庁 (NPA)", "https://www.npa.go.jp"),
    ("moj.go.jp", "出入国在留管理庁", "https://www.moj.go.jp"),
    ("JLPT", "日本語能力試験 (JLPT)", "https://www.jlpt.jp"),
    ("jpf.go.jp", "国際交流基金 (JF)", "https://www.jpf.go.jp"),
    ("nisshinkyo", "日本語教育振興協会", "https://www.nisshinkyo.org"),
    ("jta.or.jp", "全日本トラック協会 (JTA)", "https://www.jta.or.jp"),
    ("mufg", "三菱UFJ銀行 (MUFG)", "https://www.bk.mufg.jp"),
    ("boj.or.jp", "日本銀行 (BoJ)", "https://www.boj.or.jp"),
    ("mext.go.jp", "文部科学省 (MEXT)", "https://www.mext.go.jp"),
    ("mhlw.go.jp", "厚生労働省 (MHLW)", "https://www.mhlw.go.jp"),
    ("ur-net.go.jp", "UR都市機構", "https://www.ur-net.go.jp"),
    ("mlit.go.jp", "国土交通省 (MLIT)", "https://www.mlit.go.jp"),
    ("houterasu", "法テラス", "https://www.houterasu.or.jp"),
    ("fresc", "FRESC", "https://www.moj.go.jp/isa/support/fresc"),
    ("mofa.go.jp", "外務省 (MOFA)", "https://www.mofa.go.jp"),
    ("nta.go.jp", "国税庁 (NTA)", "https://www.nta.go.jp"),
    ("jasso.go.jp", "JASSO (日本学生支援機構)", "https://www.jasso.go.jp"),
    ("e-gov", "e-Gov Japan", "https://www.e-gov.go.jp"),
]

# 编译嵌入 URL 检测正则
_URL_PATTERN = re.compile(r'(https?://[^\s\)]+)')


def parse_source_string(source: str) -> Tuple[str, Optional[str]]:
    """
    解析单个来源字符串,提取显示名称和 URL.

    返回 (display_text, url_or_none).
    """
    if not source:
        return ("", None)

    # 步骤 1: 检测内嵌 URL
    url_match = _URL_PATTERN.search(source)
    if url_match:
        url = url_match.group(1)
        # 移除 URL 部分,获取显示名称
        display = _URL_PATTERN.sub('', source).strip()
        # 清理分隔符 (— / - 在 URL 前可能残留)
        display = re.sub(r'\s*[—\-]\s*$', '', display).strip()
        return (display or source, url)

    # 步骤 2: 查询内置映射表 (按关键词匹配)
    for keyword, display_name, url in SOURCE_URL_MAP:
        if keyword.lower() in source.lower():
            return (source, url)

    # 步骤 3: 无 URL,保持纯文本
    return (source, None)


def parse_source_attribution(sources: List[str]) -> List[Tuple[str, Optional[str]]]:
    """
    解析来源归因列表.

    返回 [(display_text, url_or_none), ...].
    """
    return [parse_source_string(s) for s in sources]


def render_source_as_html(source: str) -> str:
    """
    将来源字符串渲染为 HTML (含可链接或纯文本).
    """
    display, url = parse_source_string(source)
    if url:
        return f'<a href="{url}" target="_blank" rel="noopener noreferrer" style="color:inherit;text-decoration:underline;text-decoration-style:dotted;text-underline-offset:2px;">{display}</a>'
    return source


def render_source_list_as_html(sources: List[str], separator: str = " | ") -> str:
    """
    将来源列表渲染为 HTML,使用 separator 分隔.
    """
    if not sources:
        return ""
    parts = [render_source_as_html(s) for s in sources]
    return separator.join(parts)


def render_source_ul_as_html(sources: List[str]) -> str:
    """
    将来源列表渲染为 <ul><li> 列表.
    """
    if not sources:
        return ""
    items = []
    for s in sources:
        display, url = parse_source_string(s)
        if url:
            items.append(
                f'<li>{display} — <a href="{url}" target="_blank" rel="noopener noreferrer" '
                f'style="color:#1565c0;text-decoration:underline;text-decoration-style:dotted;">'
                f'{url}</a></li>'
            )
        else:
            items.append(f"<li>{display}</li>")
    return "\n".join(items)


if __name__ == "__main__":
    # 快速测试
    test_sources = [
        "Gartner — Market Guide for AI Security (Sept 2025)",
        "IDC — MEA Cybersecurity Market Forecast 10/2025",
        "(一財)日本自動車連盟(JAF) — https://www.jaf.or.jp/",
        "Mandiant (Google) — M-Trends 2025 MEA Special Report",
        "Smart Dubai — Annual Report 2024-2025",
        "Some unknown source without URL",
    ]
    print("=== HTML 渲染测试 ===")
    for s in test_sources:
        html = render_source_as_html(s)
        print(f"  {html}")
    print("\n=== 列表渲染 ===")
    print(render_source_ul_as_html(test_sources))
