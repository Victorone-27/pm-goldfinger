#!/usr/bin/env python3
"""Manage a user LaunchAgent. Never put API keys into its plist."""

import argparse
import os
import plistlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LABEL = "com.pm-goldfinger.competitor-weekly"


def definition(root: Path, interpreter: str, no_llm: bool) -> dict:
    return {
        "Label": LABEL,
        "ProgramArguments": [interpreter, str(root / "run_weekly.py")] + (["--no-llm"] if no_llm else []),
        "WorkingDirectory": str(root),
        "StartCalendarInterval": {"Weekday": 1, "Hour": 9, "Minute": 0},
        "RunAtLoad": False,
        "StandardOutPath": str(root / "data" / "logs" / "launchd.stdout.log"),
        "StandardErrorPath": str(root / "data" / "logs" / "launchd.stderr.log"),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="周一上午 9 点运行（以 macOS 系统时区为准）")
    parser.add_argument("action", choices=["install", "uninstall"])
    parser.add_argument("--preview", action="store_true", help="只展示配置，不写文件、不注册任务")
    parser.add_argument("--no-llm", action="store_true", help="定时任务始终跳过模型")
    args = parser.parse_args(argv)
    # Preserve the venv executable path; resolving symlinks would bypass its packages.
    content = plistlib.dumps(definition(ROOT, os.path.abspath(sys.executable), args.no_llm))
    if args.preview:
        if args.action == "install":
            sys.stdout.buffer.write(content)
        else:
            print(f"将卸载用户任务 {LABEL} 并删除其 plist，保留快照、周报和日志。")
        return 0
    if sys.platform != "darwin":
        print("安装和卸载仅支持 macOS。", file=sys.stderr)
        return 1
    path = Path.home() / "Library" / "LaunchAgents" / f"{LABEL}.plist"
    domain = f"gui/{os.getuid()}"
    if args.action == "install":
        if path.exists() or subprocess.run(["launchctl", "print", f"{domain}/{LABEL}"], capture_output=True).returncode == 0:
            print("任务或配置已存在，请先卸载后再安装。", file=sys.stderr)
            return 1
        (ROOT / "data" / "logs").mkdir(parents=True, exist_ok=True)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream:
            stream.write(content)
        result = subprocess.run(["launchctl", "bootstrap", domain, str(path)], capture_output=True)
        if result.returncode:
            path.unlink()
            print("launchd 注册失败，已移除本次生成的配置。请确认当前用户有图形登录会话。", file=sys.stderr)
            return 1
        print("已安装：每周一上午 9:00（macOS 系统时区）；安装时不会立即执行。")
    else:
        loaded = subprocess.run(["launchctl", "print", f"{domain}/{LABEL}"], capture_output=True).returncode == 0
        if loaded:
            result = subprocess.run(["launchctl", "bootout", f"{domain}/{LABEL}"], capture_output=True)
            if result.returncode:
                print("卸载失败，保留配置文件。", file=sys.stderr)
                return 1
        if path.exists():
            path.unlink()
        print("任务已卸载或原本未安装；快照、周报和日志已保留。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
