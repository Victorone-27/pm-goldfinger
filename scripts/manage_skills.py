#!/usr/bin/env python3
"""Install repo-owned Skill symlinks without replacing other user files."""

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def ready_skills() -> tuple[dict[str, Path], list[str]]:
    ready, skipped = {}, []
    for directory in sorted((REPO / "skills").iterdir()):
        path = directory / "SKILL.md"
        if not path.is_file():
            continue
        content = path.read_text(encoding="utf-8")
        header = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", content, re.DOTALL)
        if not header:
            skipped.append(directory.name)
            continue
        # These owned Skill entrypoints use plain, single-line name/description fields.
        name_match = re.search(r"^name:\s*([a-z0-9-]+)\s*$", header[1], re.MULTILINE)
        description = re.search(r"^description:\s*\S.+$", header[1], re.MULTILINE)
        if not name_match or not description or name_match[1] != directory.name:
            raise ValueError(f"Skill 元数据无效或名称与目录不符：{directory.name}")
        ready[directory.name] = directory.resolve()
    return ready, skipped


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="预览并确认安装/卸载本项目已完成的 Skills")
    parser.add_argument("--target", choices=["codex", "claude", "all"], default="all")
    parser.add_argument("--skill", action="append", help="指定 Skill，可重复；默认处理所有已完成 Skill")
    parser.add_argument("--uninstall", action="store_true", help="只移除指向本仓库的软链接")
    parser.add_argument("--dry-run", action="store_true", help="仅打印计划，不创建或移除文件")
    parser.add_argument("--yes", action="store_true", help="已确认的自动化操作：打印计划后直接执行")
    parser.add_argument("--codex-dir", type=Path, default=Path.home() / ".agents/skills", help="Codex 安装目录；可用于隔离验证")
    parser.add_argument("--claude-dir", type=Path, default=Path.home() / ".claude/skills", help="Claude Code 安装目录；可用于隔离验证")
    args = parser.parse_args(argv)
    created = []
    try:
        ready, skipped = ready_skills()
        selected = sorted(set(args.skill or ready))
        for name in selected:
            if name not in ready:
                raise ValueError(f"Skill 不存在或尚未完成：{name}")
        if not selected:
            raise ValueError("没有可安装的 Skill。")
        roots = {"codex": args.codex_dir.expanduser().absolute(), "claude": args.claude_dir.expanduser().absolute()}
        targets = [args.target] if args.target != "all" else ["codex", "claude"]
        plan, visited = [], set()
        for target in targets:
            for name in selected:
                source = ready[name]
                destination = roots[target] / name
                if destination in visited:
                    continue
                visited.add(destination)
                exists = destination.exists() or destination.is_symlink()
                owned = destination.is_symlink() and destination.resolve() == source
                if exists and not owned:
                    raise ValueError(f"目标已有其他文件或链接，不覆盖也不删除：{destination}")
                action = "移除链接" if args.uninstall and owned else "创建链接" if not args.uninstall and not exists else "无需变更"
                plan.append((action, destination, source))
        if skipped:
            print("跳过未完成的占位 Skill：" + "、".join(skipped))
        print("本次计划：")
        for action, destination, source in plan:
            print(f"- {action}：{destination} → {source}")
        if args.dry_run:
            print("仅预览，未修改文件。")
            return 0
        if all(action == "无需变更" for action, _, _ in plan):
            print("已是目标状态，未修改文件。")
            return 0
        if not args.yes:
            try:
                accepted = input("确认执行以上计划？输入 y 继续，其他输入取消：").strip().lower() == "y"
            except EOFError:
                accepted = False
            if not accepted:
                print("已取消，未修改文件。")
                return 0
        for action, destination, source in plan:
            if action == "创建链接":
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.symlink_to(source, target_is_directory=True)
                created.append((destination, source))
            elif action == "移除链接":
                # Recheck ownership before removal, including changes made during the prompt.
                if not destination.is_symlink() or destination.resolve() != source:
                    raise ValueError(f"目标在确认期间发生变化，停止移除：{destination}")
                destination.unlink()
        print("已完成。仓库源文件和其他 Skills 保持原样。")
        return 0
    except (OSError, ValueError) as error:
        for destination, source in reversed(created):
            if destination.is_symlink() and destination.resolve() == source:
                destination.unlink()
        print(f"未完成：{error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
