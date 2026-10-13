import fcntl
import json
import os
import tempfile
from contextlib import contextmanager
from datetime import date
from pathlib import Path


def read_snapshot(path: Path) -> dict:
    snapshot = json.loads(path.read_text(encoding="utf-8"))
    if snapshot.get("schema_version") != 1 or not isinstance(snapshot.get("apps"), list) or not snapshot["apps"]:
        raise ValueError(f"快照格式错误：{path.name}")
    date.fromisoformat(snapshot["date"])
    ids = [app["app_id"] for app in snapshot["apps"]]
    if len(set(ids)) != len(ids):
        raise ValueError(f"快照 App ID 重复：{path.name}")
    return snapshot


def previous_snapshot(directory: Path, current_date: date, country: str) -> dict | None:
    # Today's file is never a comparison baseline, keeping same-day reruns stable.
    candidates = []
    for path in directory.glob("????-??-??.json"):
        try:
            observed_date = date.fromisoformat(path.stem)
        except ValueError:
            continue
        if observed_date < current_date:
            candidates.append(path)
    for path in sorted(candidates, reverse=True):
        snapshot = read_snapshot(path)
        if snapshot["country"] == country and not snapshot.get("synthetic", False):
            if snapshot["date"] != path.stem:
                raise ValueError(f"快照日期与文件名不一致：{path.name}")
            return snapshot
    return None


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(dir=path.parent, prefix=".writing-")
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(content)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


@contextmanager
def run_lock(data_dir: Path):
    data_dir.mkdir(parents=True, exist_ok=True)
    with (data_dir / ".run.lock").open("a") as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError("已有周报任务运行中，请稍后重试。") from None
        try:
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)
