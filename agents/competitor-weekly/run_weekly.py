#!/usr/bin/env python3
"""Compare App Store snapshots and produce a Chinese weekly report."""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from src.config import load_config
from src.diff import compare
from src.fetch import AppStoreClient, FetchError
from src.report import render, week_label
from src.snapshot import atomic_write, previous_snapshot, read_snapshot, run_lock
from src.summarize import summarize

ROOT = Path(__file__).resolve().parent


def generate(current: dict, previous: dict | None, config: dict, no_llm: bool) -> str:
    changes = compare(current, previous)
    summary = summarize(changes, config["llm"], ROOT / "prompts", no_llm=no_llm)
    return render(current, previous, changes, summary)


def run(args, config: dict) -> Path | None:
    if args.dry_run:
        previous = read_snapshot(ROOT / "fixtures" / "week1.json")
        current = read_snapshot(ROOT / "fixtures" / "week2.json")
        # Offline fixtures never enter the real snapshots/reports or call a model.
        path = ROOT / "reports" / "dry-run" / f"{week_label(current['date'])}.md"
        atomic_write(path, generate(current, previous, config, no_llm=True))
        return path
    client = AppStoreClient(config["network"], config["country"])
    missing_ids = any(app.get("app_id") is None for app in config["apps"])
    if args.search or missing_ids:
        for app in config["apps"]:
            print(f"\n{app['name']}：候选（请确认名称、开发者、ID 与商店链接）")
            print(json.dumps(client.search(app["search_term"]), ensure_ascii=False, indent=2))
        print("\n确认后再手动将 App ID 写入 config.yaml；搜索不会修改配置。")
        if missing_ids and not args.search:
            raise ValueError("App ID 尚未全部确认，未生成快照或周报。")
        return None
    with run_lock(ROOT / "data"):
        observed_at = datetime.now(ZoneInfo(config["timezone"]))
        directory = ROOT / "data" / "snapshots"
        previous = previous_snapshot(directory, observed_at.date(), config["country"])
        # Complete all lookups before writing anything. A failed app isn't 'unchanged'.
        current = {
            "schema_version": 1, "country": config["country"], "synthetic": False,
            "date": observed_at.date().isoformat(), "observed_at": observed_at.isoformat(timespec="seconds"),
            "baseline_date": previous["date"] if previous else None,
            "apps": [client.lookup(app) for app in config["apps"]],
        }
        report = generate(current, previous, config, no_llm=args.no_llm)
        path = ROOT / "reports" / f"{week_label(current['date'])}.md"
        # Write report first: failed report writes must not advance the baseline.
        atomic_write(path, report)
        atomic_write(directory / f"{current['date']}.json", json.dumps(current, ensure_ascii=False, indent=2) + "\n")
        return path


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="中国区 App Store 竞品周报")
    parser.add_argument("--config", type=Path, default=ROOT / "config.yaml", help="配置文件路径")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--dry-run", action="store_true", help="使用两周虚构测试数据，全程不联网")
    modes.add_argument("--search", action="store_true", help="查找 App 候选，不修改配置")
    parser.add_argument("--no-llm", action="store_true", help="跳过模型，仅展示原文")
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
        result = run(args, config)
    except (FetchError, ValueError, KeyError, TypeError, OSError) as error:
        # No tracebacks or raw network/API exceptions that may include credentials.
        message = str(error) if isinstance(error, (FetchError, ValueError)) else "配置或本地文件不可用，请检查文件与权限。"
        print(f"未完成：{message}", file=sys.stderr)
        return 1
    if result is not None:
        print(f"周报已生成：{result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
