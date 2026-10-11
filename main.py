# -*- coding: utf-8 -*-
"""
main.py - Prompt-Driven Intelligence Engine CLI

以提示词（Prompt）为核心驱动的分析引擎入口。
所有业务逻辑由 prompts/*.yaml 定义驱动，代码仅负责调度。

用法:
    python main.py --list                        # 列出所有 Prompt
    python main.py --keyword 半导体               # 查看匹配的 Prompt
    python main.py --keyword 半导体 --run         # 执行分析并生成报告
    python main.py --prompt tech_ai --run         # 直接指定 Prompt ID 执行
    python main.py --vertical tech --run          # 执行某赛道全部 Prompt
    python main.py --health                       # 健康检查
    python main.py --benchmark                    # 基准测试：跑一遍所有 Prompt
"""

from __future__ import annotations

import os
import sys
if sys.platform == 'win32':
    os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

import argparse
import time
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from config.settings import REPORTS_DIR
from src.prompt_registry import PromptRegistry, get_registry

console = Console()


# ── 命令实现 ──

def cmd_list(args):
    """列出所有 Prompt."""
    registry = get_registry()
    if args.vertical:
        prompts = registry.list_by_vertical(args.vertical)
        console.print(f"\n[bold cyan]{args.vertical.upper()} 赛道 Prompt 列表[/bold cyan]\n")
    elif args.enabled:
        prompts = registry.list_enabled()
        console.print("\n[bold cyan]所有已启用 Prompt[/bold cyan]\n")
    else:
        prompts = registry.list_all()
        console.print("\n[bold cyan]所有 Prompt 定义[/bold cyan]\n")

    if not prompts:
        console.print("[dim]无可用的 Prompt 定义。请检查 prompts/ 目录。[/dim]")
        return

    table = Table(show_header=True, header_style="bold magenta", box=None)
    table.add_column("ID", style="cyan", min_width=22)
    table.add_column("赛道", min_width=8)
    table.add_column("名称(中)", min_width=20)
    table.add_column("地区", min_width=6)
    table.add_column("调度", min_width=8)
    table.add_column("数据", min_width=5)
    table.add_column("维度", min_width=5)
    table.add_column("启用", min_width=4)

    for p in prompts:
        table.add_row(
            p.id, p.vertical, p.label_zh[:30], p.region_zh[:6],
            p.schedule_cadence, str(len(p.data_pipes)),
            str(len(p.analysis_dimensions)), "Y" if p.enabled else "N",
        )
    console.print(table)

    s = registry.summary()
    console.print(
        f"\n[dim]共 {s['total']} 个 Prompt ({s['enabled']} 个启用) | "
        f"宏观 {s['by_vertical']['macro']} 科技 {s['by_vertical']['tech']} "
        f"房地产 {s['by_vertical']['realestate']} 移民 {s['by_vertical']['migration']}[/dim]"
    )


def cmd_run(args):
    """执行 Prompt."""
    from src.prompt_runtime import get_runtime

    registry = get_registry()
    runtime = get_runtime()

    prompts = _collect_prompts(args, registry)
    if not prompts:
        console.print("[yellow]未匹配到任何 Prompt。[/yellow]")
        console.print("提示: [cyan]python main.py --list[/cyan] 查看可用 Prompt。")
        return

    console.print(f"\n[bold green]准备执行 {len(prompts)} 个 Prompt[/bold green]\n")

    results = []
    for p in prompts:
        console.print(f"[bold]>> {p.id} ({p.label_zh})[/bold]")
        start = time.time()
        path = runtime.execute(p)
        elapsed = time.time() - start
        if path:
            results.append((p.id, path, elapsed))
            console.print(f"  [green][OK] [{elapsed:.1f}s] {path}[/green]")
        else:
            console.print(f"  [red][FAIL] ({elapsed:.1f}s)[/red]")

    console.print(f"\n[bold]完成: {len(results)}/{len(prompts)} 成功[/bold]")


def cmd_show(args):
    """查看 Prompt 详情."""
    import yaml
    registry = get_registry()
    p = registry.get(args.prompt_id)
    if not p:
        console.print(f"[red]Prompt 未找到: {args.prompt_id}[/red]")
        return

    console.print(f"\n[bold cyan]Prompt 定义 [{p.id}][/bold cyan]")
    console.print(f"[bold]名称:[/bold] {p.label_zh} / {p.label_en}")
    console.print(f"[bold]赛道:[/bold] {p.vertical}  |  [bold]版本:[/bold] v{p.version}  |  [bold]启用:[/bold] {'Yes' if p.enabled else 'No'}")
    console.print(f"[bold]地区:[/bold] {p.region_zh} / {p.region_en}")
    console.print(f"[bold]描述:[/bold] {p.description_zh}")

    console.print(f"\n[bold]触发词({len(p.triggers)}):[/bold]")
    for t in p.triggers[:10]:
        console.print(f"  * {t}")
    if len(p.triggers) > 10:
        console.print(f"  [dim]... 共 {len(p.triggers)} 个[/dim]")

    console.print(f"\n[bold]数据管道 ({len(p.data_pipes)}):[/bold]")
    for dp in p.data_pipes:
        console.print(f"  * {dp.pipe}")

    console.print(f"\n[bold]分析维度 ({len(p.analysis_dimensions)}):[/bold]")
    for d in p.analysis_dimensions:
        console.print(f"  * {d.label_zh} [{d.method}]")

    console.print(f"\n[bold]调度:[/bold] {p.schedule_cadence} @ {p.schedule_time}")
    console.print(f"[bold]模板:[/bold] {p.report_template} -> {p.report_output_dir}")

    if args.yaml:
        console.print(f"\n[dim]{'='*60}[/dim]")
        console.print(yaml.dump(p.raw, allow_unicode=True, default_flow_style=False))


def cmd_health(args):
    """健康检查."""
    console.print("\n[bold cyan]健康检查[/bold cyan]\n")

    # Registry
    try:
        registry = get_registry()
        s = registry.summary()
        console.print(f"[OK] PromptRegistry: {s['total']} prompts ({s['enabled']} enabled)")
    except Exception as e:
        console.print(f"[FAIL] PromptRegistry: {e}")

    # Data Engine
    try:
        from src.data_engine import get_runner
        runner = get_runner()
        pipes = runner.list_pipes()
        console.print(f"[OK] DataEngine: {len(pipes)} pipes ready")
    except Exception as e:
        console.print(f"[FAIL] DataEngine: {e}")

    # Runtime
    try:
        from src.prompt_runtime import get_runtime
        _ = get_runtime()
        console.print("[OK] PromptRuntime: initialized")
    except Exception as e:
        console.print(f"[FAIL] PromptRuntime: {e}")

    # Renderers
    try:
        from src.renderers import RendererFactory
        console.print(f"[OK] Renderers: {', '.join(RendererFactory.list_templates())}")
    except Exception as e:
        console.print(f"[FAIL] Renderers: {e}")

    # Reports dir
    if REPORTS_DIR.exists():
        n = len(list(REPORTS_DIR.rglob("*.html")))
        console.print(f"[OK] Reports: {REPORTS_DIR} ({n} existing)")
    else:
        console.print(f"[WARN] Reports dir not found: {REPORTS_DIR}")

    # Pipe coverage check
    try:
        registry = get_registry()
        runner = get_runner()
        pipes_needed = set()
        for p in registry.list_enabled():
            for dp in p.data_pipes:
                pipes_needed.add(dp.pipe)
        available = set(runner.list_pipes())
        missing = pipes_needed - available
        if missing:
            console.print(f"[WARN] Missing pipes: {', '.join(missing)}")
        else:
            console.print(f"[OK] All {len(pipes_needed)} required pipes registered")
    except Exception as e:
        console.print(f"[WARN] Pipe check: {e}")


def cmd_benchmark(args):
    """基准测试: 跑一遍所有启用 Prompt."""
    from src.prompt_runtime import get_runtime
    registry = get_registry()
    runtime = get_runtime()
    prompts = registry.list_enabled()

    console.print(f"\n[bold cyan]Benchmark: {len(prompts)} prompts[/bold cyan]\n")
    start = time.time()
    ok, fail = 0, 0
    for p in prompts:
        console.print(f"  >> {p.id}...", end="")
        result = runtime.execute(p)
        if result:
            console.print(f"  [green]OK[/green]")
            ok += 1
        else:
            console.print(f"  [red]FAIL[/red]")
            fail += 1

    console.print(f"\nDone: {ok} ok, {fail} fail, {time.time()-start:.1f}s")


# ── 辅助函数 ──

def _collect_prompts(args, registry: PromptRegistry):
    """从各种参数中收集要执行的 Prompts."""
    prompts = []
    seen = set()

    def add(p):
        if p and p.id not in seen and p.enabled:
            seen.add(p.id)
            prompts.append(p)

    # --prompt 直接指定 ID
    if args.prompt:
        for pid in args.prompt:
            add(registry.get(pid))

    # --keyword 模糊匹配
    if args.keyword:
        for kw in args.keyword:
            add(registry.resolve(kw, vertical=args.vertical))

    # --macro/--tech/--realestate/--migration 赛道批量
    if args.macro:
        for p in registry.list_by_vertical("macro"):
            add(p)
    if args.tech:
        for p in registry.list_by_vertical("tech"):
            add(p)
    if args.realestate:
        for p in registry.list_by_vertical("realestate"):
            add(p)
    if args.migration:
        for p in registry.list_by_vertical("migration"):
            add(p)

    return prompts


# ── CLI 构建 ──

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="intelkb",
        description="IntelKB Prompt-Driven Intelligence Engine - 以提示词为核心的全球经济/行业分析系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py --list                          # 列出所有 Prompt
  python main.py --keyword 半导体 --run           # 执行半导体分析
  python main.py --keyword 迪拜 房产 --run        # 组合关键词
  python main.py --prompt tech_ai --run          # 直接指定 Prompt ID
  python main.py --vertical tech --run           # 执行科技赛道全部
  python main.py --health                        # 健康检查
  python main.py --benchmark                     # 基准测试
        """,
    )

    parser.add_argument("--keyword", "-k", nargs="+", action="append",
                        help="关键词，可多次指定")
    parser.add_argument("--prompt", "-p", nargs="+", action="append",
                        help="直接指定 Prompt ID")
    parser.add_argument("--vertical", "-v",
                        choices=["macro", "tech", "realestate", "migration"],
                        help="赛道筛选")
    parser.add_argument("--macro", action="store_true", help="运行宏观 Prompt")
    parser.add_argument("--tech", action="store_true", help="运行科技 Prompt")
    parser.add_argument("--realestate", action="store_true", help="运行房地产 Prompt")
    parser.add_argument("--migration", action="store_true", help="运行移民 Prompt")

    parser.add_argument("--list", action="store_true", help="列出所有 Prompt")
    parser.add_argument("--enabled", action="store_true", help="仅显示已启用 Prompt")
    parser.add_argument("--run", action="store_true", help="执行匹配的 Prompt")
    parser.add_argument("--show", metavar="PROMPT_ID", help="查看 Prompt 详情")
    parser.add_argument("--yaml", action="store_true", help="显示原始 YAML")
    parser.add_argument("--health", action="store_true", help="健康检查")
    parser.add_argument("--benchmark", action="store_true", help="基准测试")
    parser.add_argument("--no-cache", action="store_true", help="禁用数据缓存")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    # 扁平化列表参数
    args.keyword = [x for sub in (args.keyword or []) for x in sub]
    args.prompt = [x for sub in (args.prompt or []) for x in sub]

    # 快捷命令
    if args.health:
        cmd_health(args)
        return
    if args.benchmark:
        cmd_benchmark(args)
        return
    if args.show:
        cmd_show(argparse.Namespace(prompt_id=args.show, yaml=args.yaml))
        return

    has_filter = args.keyword or args.prompt or args.vertical or args.macro or args.tech or args.realestate or args.migration
    has_action = args.run

    if has_filter and has_action:
        cmd_run(args)
    elif has_filter:
        cmd_list(args)
    elif args.list:
        cmd_list(args)
    else:
        console.print(
            Panel.fit(
                "[bold green]IntelKB Prompt-Driven Intelligence Engine[/bold green]\n\n"
                "以提示词为核心的全球经济与行业分析报告系统\n\n"
                "[cyan]用法:[/cyan]\n"
                "  python main.py --list\n"
                "  python main.py --keyword 半导体 --run\n"
                "  python main.py --keyword 迪拜 房产 --run\n"
                "  python main.py --vertical tech --run\n"
                "  python main.py --health\n",
                title="IntelKB",
                border_style="green",
            )
        )


if __name__ == "__main__":
    main()
