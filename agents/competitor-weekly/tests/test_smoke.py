import copy
import json
import shutil
from pathlib import Path
from urllib.error import URLError

import pytest

import run_weekly
from src import summarize as llm
from src.config import load_config
from src.fetch import AppStoreClient

ROOT = Path(__file__).resolve().parents[1]


def forbidden(*args, **kwargs):
    raise AssertionError("Unexpected external call or write")


@pytest.fixture
def isolated_smoke(tmp_path, monkeypatch):
    shutil.copytree(ROOT / "prompts", tmp_path / "prompts")
    for relative in ["data/snapshots/2026-10-13.json", "reports/2026-W42.md"]:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("已有内容不可改动")
    monkeypatch.setattr(run_weekly, "ROOT", tmp_path)
    monkeypatch.setattr(run_weekly, "read_api_key", lambda: "smoke-test-placeholder")
    monkeypatch.setattr(run_weekly, "atomic_write", forbidden)
    monkeypatch.setattr(run_weekly, "run_lock", forbidden)
    config = load_config(ROOT / "config.yaml")
    doubao = next(app for app in config["apps"] if app["name"] == "豆包")
    current = {"app_id": doubao["app_id"], "name": "豆包", "version": "test-current-version",
               "release_notes": "虚构测试原文：新增回答收藏功能。", "url": "https://example.com/smoke-fixture"}
    lookups = []

    def lookup(self, app):
        lookups.append(copy.deepcopy(app))
        return copy.deepcopy(current)

    monkeypatch.setattr(AppStoreClient, "lookup", lookup)
    before = {str(path.relative_to(tmp_path)): path.read_bytes() for path in tmp_path.rglob("*") if path.is_file()}
    yield current, lookups
    after = {str(path.relative_to(tmp_path)): path.read_bytes() for path in tmp_path.rglob("*") if path.is_file()}
    assert after == before


def response_for(current):
    evidence = "新增回答收藏功能"
    result = {"headline": "新增回答收藏功能", "highlight_app_id": current["app_id"], "headline_evidence": evidence,
              "items": [{"app_id": current["app_id"], "points": [{"text": "可以收藏回答", "evidence": evidence}]}]}
    return {"choices": [{"finish_reason": "stop", "message": {"content": json.dumps(result)}}],
            "usage": {"prompt_tokens": 120, "completion_tokens": 30, "total_tokens": 150}}


def test_smoke_calls_once_with_current_doubao_notes_and_prints_tokens(isolated_smoke, monkeypatch, capsys):
    current, lookups = isolated_smoke
    calls = []

    def respond(config, payload, key):
        calls.append(payload)
        assert key == "smoke-test-placeholder"
        return response_for(current)

    monkeypatch.setattr(llm, "_post", respond)
    assert run_weekly.main(["--config", str(ROOT / "config.yaml"), "--llm-smoke-test"]) == 0
    assert len(calls) == 1 and [app["name"] for app in lookups] == ["豆包"]
    assert current["release_notes"] in calls[0]["messages"][1]["content"]
    output = capsys.readouterr()
    assert "可以收藏回答" in output.out and "输入 120，输出 30，合计 150" in output.out
    assert "冒烟测试通过" in output.out and "smoke-test-placeholder" not in output.out + output.err


def test_smoke_missing_key_fails_without_network(isolated_smoke, monkeypatch, capsys):
    monkeypatch.setattr(run_weekly, "read_api_key", lambda: None)
    monkeypatch.setattr(AppStoreClient, "lookup", forbidden)
    monkeypatch.setattr(llm, "_post", forbidden)
    assert run_weekly.main(["--config", str(ROOT / "config.yaml"), "--llm-smoke-test"]) == 1
    assert "请先配置" in capsys.readouterr().err


@pytest.mark.parametrize("failure", ["network", "invalid_json", "truncated", "missing_usage"])
def test_smoke_failure_never_claims_success_or_retries(isolated_smoke, monkeypatch, capsys, failure):
    current, _ = isolated_smoke
    calls = []

    def respond(config, payload, key):
        calls.append(payload)
        if failure == "network":
            raise URLError("private-response-smoke-test-placeholder")
        response = response_for(current)
        if failure == "invalid_json":
            response["choices"][0]["message"]["content"] = "not json"
        elif failure == "truncated":
            response["choices"][0]["finish_reason"] = "length"
        elif failure == "missing_usage":
            response.pop("usage")
        return response

    monkeypatch.setattr(llm, "_post", respond)
    assert run_weekly.main(["--config", str(ROOT / "config.yaml"), "--llm-smoke-test"]) == 1
    assert len(calls) == 1
    output = capsys.readouterr()
    assert "冒烟测试通过" not in output.out
    assert "private-response" not in output.out + output.err
    assert "smoke-test-placeholder" not in output.out + output.err
    if failure in ("invalid_json", "truncated"):
        assert "输入 120，输出 30，合计 150" in output.out
    else:
        assert "无法确认消耗" in output.out


def test_smoke_rejects_no_llm_before_any_call(monkeypatch):
    monkeypatch.setattr(run_weekly, "read_api_key", forbidden)
    with pytest.raises(SystemExit) as error:
        run_weekly.main(["--llm-smoke-test", "--no-llm"])
    assert error.value.code == 2
