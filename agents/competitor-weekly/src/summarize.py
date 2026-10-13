import json
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

from .credentials import read_api_key


MISSING_KEY = "环境变量 DEEPSEEK_API_KEY 和 macOS 钥匙串均未提供可用密钥，直接保留原文"


def _fallback(reason: str, usage: dict | None = None) -> dict:
    return {"headline": None, "items": {}, "reason": reason, "usage": usage}


def _post(config: dict, payload: dict, api_key: str) -> dict:
    request = Request(
        config["base_url"].rstrip("/") + "/chat/completions",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    # Do not retry paid calls or log headers, response bodies, or exception strings.
    with urlopen(request, timeout=config["timeout_seconds"]) as response:
        return json.load(response)


def _validate(result: dict, notes: list[dict]) -> dict:
    sources = {row["app_id"]: row["release_notes"] for row in notes}
    highlight = result["highlight_app_id"]
    if highlight not in sources or not isinstance(result["headline"], str) or not result["headline"].strip():
        raise ValueError("Invalid headline")
    evidence = result["headline_evidence"]
    if not isinstance(evidence, str) or not evidence.strip() or evidence not in sources[highlight]:
        raise ValueError("Unverifiable headline")
    items, found = {}, set()
    for item in result["items"]:
        app_id = item["app_id"]
        if app_id not in sources or app_id in found or not 1 <= len(item["points"]) <= 3:
            raise ValueError("Invalid item")
        found.add(app_id)
        for point in item["points"]:
            if not isinstance(point["text"], str) or not point["text"].strip():
                raise ValueError("Invalid point")
            evidence = point["evidence"]
            if not isinstance(evidence, str) or not evidence.strip() or evidence not in sources[app_id]:
                raise ValueError("Unverifiable point")
        items[app_id] = item["points"]
    if found != set(sources):
        raise ValueError("Missing items")
    return {"headline": result["headline"], "highlight_app_id": highlight,
            "headline_evidence": result["headline_evidence"], "items": items, "reason": None}


def _usage(response: dict) -> dict | None:
    usage = response.get("usage") if isinstance(response, dict) else None
    keys = ("prompt_tokens", "completion_tokens", "total_tokens")
    if isinstance(usage, dict) and all(type(usage.get(key)) is int and usage[key] >= 0 for key in keys):
        return {key: usage[key] for key in keys}
    return None


def summarize_notes(notes: list[dict], config: dict, prompts: Path, api_key: str) -> dict:
    """Make at most one model call; shared by weekly reports and the smoke test."""
    notes_json = json.dumps(notes, ensure_ascii=False)
    if len(notes_json) > config["max_input_chars"]:
        return _fallback("更新说明超出输入上限，直接保留原文")
    usage = None
    try:
        system = (prompts / "summarize_system.md").read_text(encoding="utf-8")
        user = (prompts / "summarize_user.md").read_text(encoding="utf-8").replace("{{release_notes_json}}", notes_json)
        response = _post(config, {
            "model": config["model"], "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "response_format": {"type": "json_object"}, "max_tokens": config["max_tokens"], "stream": False,
        }, api_key)
        usage = _usage(response)
        choice = response["choices"][0]
        if choice.get("finish_reason") != "stop":
            raise ValueError("Incomplete model output")
        return {**_validate(json.loads(choice["message"]["content"]), notes), "usage": usage}
    except (URLError, OSError, TimeoutError, ValueError, KeyError, TypeError, IndexError):
        return _fallback("模型调用失败或输出无法核验，直接保留原文", usage)


def summarize(changes: list[dict], config: dict, prompts: Path, no_llm: bool = False) -> dict:
    notes = [{"app_id": change["app"]["app_id"], "name": change["app"]["name"],
              "release_notes": change["app"]["release_notes"]}
             for change in changes if change["notes_changed"]]
    if not notes:
        return _fallback("没有需要归纳的更新说明变化")
    if no_llm:
        return _fallback("已跳过模型，直接保留原文")
    api_key = read_api_key()
    if not api_key:
        return _fallback(MISSING_KEY)
    return summarize_notes(notes, config, prompts, api_key)
