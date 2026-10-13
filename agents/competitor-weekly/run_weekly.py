#!/usr/bin/env python3
"""Compare App Store snapshots and produce a Chinese weekly report."""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from src.config import load_config
from src.credentials import read_api_key
from src.diff import compare
from src.fetch import AppStoreClient, FetchError
from src.report import render, week_label
from src.snapshot import atomic_write, previous_snapshot, read_snapshot, run_lock
from src.summarize import summarize, summarize_notes

ROOT = Path(__file__).resolve().parent


def generate(current: dict, previous: dict | None, config: dict, no_llm: bool) -> str:
    changes = compare(current, previous)
    summary = summarize(changes, config["llm"], ROOT / "prompts", no_llm=no_llm)
    return render(current, previous, changes, summary)


def smoke_test(config: dict) -> None:
    app = next((app for app in config["apps"] if app["name"] == "豆包"), None)
    if app is None or app.get("app_id") is None:
        raise ValueError("冒烟测试需要配置已确认 App ID 的豆包。")
    api_key = read_api_key()
    if not api_key:
        raise ValueError("冒烟测试未调用模型：请先配置环境变量 DEEPSEEK_API_KEY 或钥匙串服务 pm-goldfinger-deepseek。")
    current = AppStoreClient(config["network"], config["country"]).lookup(app)
    if not current["release_notes"].strip():
        raise ValueError("豆包当前没有更新说明，未调用模型。")
    notes = [{"app_id": current["app_id"], "name": current["name"], "release_notes": current["release_notes"]}]
    result = summarize_notes(notes, config["llm"], ROOT / "prompts", api_key)
    print(f"豆包当前版本：{current['version']}\n来源：{current['url']}")
    if result["headline"]:
        print(f"归纳：{result['headline']}")
        for point in result["items"][current["app_id"]]:
            print(f"- {point['text']}（原文依据：{point['evidence']}）")
    usage = result["usage"]
    if usage is not None:
        print(f"Token 用量（API 返回）：输入 {usage['prompt_tokens']}，输出 {usage['completion_tokens']}，合计 {usage['total_tokens']}")
    else:
        print("Token 用量：API 未返回可核验的完整用量，无法确认消耗。")
    if result["reason"]:
        reason = result["reason"].removesuffix("，直接保留原文")
        raise ValueError(f"冒烟测试未通过：{reason}。本命令未写入周报或快照。")
    if usage is None:
        raise ValueError("归纳已返回，但缺少完整 token 用量，冒烟测试未通过。")
    print("冒烟测试通过；未写入周报或快照。")


def run(args, config: dict) -> Path | None:
    if args.llm_smoke_test:
        smoke_test(config)
        return None
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
    modes.add_argument("--llm-smoke-test", action="store_true", help="用豆包当前更新说明调用一次模型，打印归纳及 token 用量，不保存报告或快照")
    parser.add_argument("--no-llm", action="store_true", help="跳过模型，仅展示原文")
    args = parser.parse_args(argv)
    if args.llm_smoke_test and args.no_llm:
        parser.error("--llm-smoke-test 不能与 --no-llm 同时使用")
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
