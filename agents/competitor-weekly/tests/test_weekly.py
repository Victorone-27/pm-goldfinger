import copy
import io
import json
import shutil
from datetime import date, datetime
from pathlib import Path
from urllib.error import URLError

import pytest

import run_weekly
from src import fetch, summarize as llm
from src.config import load_config
from src.diff import compare
from src.fetch import AppStoreClient, FetchError
from src.report import render, week_label
from src.snapshot import previous_snapshot, read_snapshot

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def weeks():
    return (read_snapshot(ROOT / "fixtures" / "week1.json"), read_snapshot(ROOT / "fixtures" / "week2.json"))


@pytest.fixture
def config():
    return load_config(ROOT / "config.yaml")


def forbidden(*args, **kwargs):
    raise AssertionError("Unexpected external call")


def test_diff_version_rating_and_unchanged(weeks):
    previous, current = weeks
    changes = compare(current, previous)
    assert [change["status"] for change in changes] == ["changed", "changed", "unchanged"]
    assert changes[0]["notes_changed"]
    assert changes[0]["fields"] == ["version", "release_notes", "release_date"]
    assert changes[1]["fields"] == ["rating", "rating_count"]
    assert not changes[1]["notes_changed"]


def test_first_week_is_baseline_without_model(weeks, config, monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-only-placeholder")
    monkeypatch.setattr(llm, "_post", forbidden)
    report = run_weekly.generate(weeks[0], None, config, no_llm=False)
    assert "首周基线" in report and "尚不能判断本周发生了什么变化" in report
    assert report.count("· 首次记录") == 3
    assert "首次发布对话功能。" in report


def test_no_changes_only_one_line(weeks, config, monkeypatch):
    monkeypatch.setattr(llm, "_post", forbidden)
    assert run_weekly.generate(weeks[0], weeks[0], config, no_llm=False) == "本周无重要变化\n"


def test_missing_key_preserves_original_report(weeks, config, monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.setattr(llm, "_post", forbidden)
    report = run_weekly.generate(weeks[1], weeks[0], config, no_llm=False)
    assert "未设置 DEEPSEEK" in report
    assert weeks[1]["apps"][0]["release_notes"] in report
    assert "1.0.0 → 1.1.0" in report and "4.2 → 4.3" in report
    assert "无变化：演示助手丙。" in report


def test_model_failure_falls_back_without_error_body(weeks, config, monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-only-placeholder")
    def failing(*args):
        raise URLError("private-response-body-test-only-placeholder")
    monkeypatch.setattr(llm, "_post", failing)
    report = run_weekly.generate(weeks[1], weeks[0], config, no_llm=False)
    assert "模型调用失败或输出无法核验" in report
    assert "private-response" not in report and "test-only-placeholder" not in report
    assert weeks[1]["apps"][0]["release_notes"] in report


@pytest.mark.parametrize("valid", [True, False])
def test_model_receives_only_changed_notes_and_requires_evidence(weeks, config, monkeypatch, valid):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-only-placeholder")
    captured = []
    evidence = "新增回答收藏功能" if valid else "虚构原文证据"
    def respond(settings, payload, key):
        captured.append(payload)
        result = {"headline": "新增回答收藏功能", "highlight_app_id": 1001, "headline_evidence": evidence,
                  "items": [{"app_id": 1001, "points": [{"text": "可以收藏回答", "evidence": evidence}]}]}
        return {"choices": [{"finish_reason": "stop", "message": {"content": json.dumps(result)}}]}
    monkeypatch.setattr(llm, "_post", respond)
    summary = llm.summarize(compare(weeks[1], weeks[0]), config["llm"], ROOT / "prompts")
    user_message = captured[0]["messages"][1]["content"]
    assert "演示助手甲" in user_message
    assert "演示助手乙" not in user_message and "演示助手丙" not in user_message
    assert '"rating"' not in user_message and '"version"' not in user_message
    assert bool(summary["items"]) == valid


def test_version_bump_with_identical_notes_does_not_call_model(weeks, config, monkeypatch):
    monkeypatch.setattr(llm, "_post", forbidden)
    current = copy.deepcopy(weeks[0])
    current["apps"][0]["version"] = "1.0.1"
    report = run_weekly.generate(current, weeks[0], config, no_llm=False)
    assert "1.0.0 → 1.0.1" in report and "更新说明未变化" in report


def test_same_day_snapshot_is_never_baseline(tmp_path, weeks):
    previous, today = copy.deepcopy(weeks)
    previous["synthetic"] = today["synthetic"] = False
    for snapshot in (previous, today):
        (tmp_path / f"{snapshot['date']}.json").write_text(json.dumps(snapshot))
    assert previous_snapshot(tmp_path, date(2026, 10, 12), "cn")["date"] == "2026-10-05"
    assert previous_snapshot(tmp_path, date(2026, 10, 5), "cn") is None


def test_iso_week_year_boundary():
    assert week_label("2027-01-01") == "2026-W53"


def test_dry_run_never_calls_network_or_writes_real_snapshots(tmp_path, monkeypatch):
    shutil.copytree(ROOT / "fixtures", tmp_path / "fixtures")
    monkeypatch.setattr(run_weekly, "ROOT", tmp_path)
    monkeypatch.setattr(fetch, "urlopen", forbidden)
    monkeypatch.setattr(llm, "_post", forbidden)
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-only-placeholder")
    assert run_weekly.main(["--config", str(ROOT / "config.yaml"), "--dry-run"]) == 0
    report = (tmp_path / "reports" / "dry-run" / "2026-W42.md").read_text()
    assert "虚构测试数据" in report and "1.0.0 → 1.1.0" in report
    assert not (tmp_path / "data").exists()
    assert not (tmp_path / "reports" / "2026-W42.md").exists()


def test_fetch_retries_twice_and_spaces_requests(config, monkeypatch):
    calls, waits = [], []
    def flaky(request, timeout):
        calls.append(request.full_url)
        if len(calls) < 3:
            raise URLError("temporary")
        return io.BytesIO(b'{"results": []}')
    monkeypatch.setattr(fetch, "urlopen", flaky)
    monkeypatch.setattr(fetch.time, "monotonic", lambda: 0)
    monkeypatch.setattr(fetch.time, "sleep", waits.append)
    assert AppStoreClient(config["network"]).search("测试") == []
    assert len(calls) == 3 and waits == [3, 3]
    assert all("country=cn" in url and "entity=software" in url for url in calls)


def test_failed_fetch_does_not_overwrite_existing_data(tmp_path, weeks, config, monkeypatch):
    monkeypatch.setattr(run_weekly, "ROOT", tmp_path)
    monkeypatch.setattr(AppStoreClient, "lookup", lambda self, app: (_ for _ in ()).throw(FetchError("模拟抓取失败")))
    snapshots = tmp_path / "data" / "snapshots"
    snapshots.mkdir(parents=True)
    previous = copy.deepcopy(weeks[0])
    previous["synthetic"] = False
    snapshot_path = snapshots / "2026-10-05.json"
    snapshot_path.write_text(json.dumps(previous))
    report_dir = tmp_path / "reports"
    report_dir.mkdir()
    report_path = report_dir / "2026-W42.md"
    report_path.write_text("原有报告")
    original = snapshot_path.read_bytes()
    assert run_weekly.main(["--config", str(ROOT / "config.yaml"), "--no-llm"]) == 1
    assert report_path.read_text() == "原有报告"
    assert snapshot_path.read_bytes() == original
    assert len(list(snapshots.iterdir())) == 1


def test_search_does_not_write_config(config, monkeypatch, capsys):
    original = (ROOT / "config.yaml").read_bytes()
    monkeypatch.setattr(AppStoreClient, "search", lambda self, term: [{"trackId": 1001, "trackName": "虚构候选"}])
    assert run_weekly.main(["--search"]) == 0
    assert "搜索不会修改配置" in capsys.readouterr().out
    assert (ROOT / "config.yaml").read_bytes() == original
