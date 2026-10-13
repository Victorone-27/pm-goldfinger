from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

import yaml


def load_config(path: Path) -> dict:
    try:
        config = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        raise ValueError("配置不是有效的 YAML，请检查缩进和字段格式。") from None
    if not isinstance(config, dict) or config.get("country") != "cn":
        raise ValueError("配置 country 必须为 cn。")
    ZoneInfo(config["timezone"])
    apps = config.get("apps")
    if not isinstance(apps, list) or not apps:
        raise ValueError("至少配置一个 App。")
    ids, names = set(), set()
    for app in apps:
        if not isinstance(app, dict):
            raise ValueError("每个 App 必须包含 name、search_term 和 app_id 字段。")
        for key in ("name", "search_term"):
            if not isinstance(app.get(key), str) or not app[key].strip():
                raise ValueError(f"App 缺少 {key}。")
        app_id = app.get("app_id")
        if app_id is not None and (type(app_id) is not int or app_id <= 0):
            raise ValueError("app_id 必须为已确认的正整数或 null。")
        if app["name"] in names or (app_id is not None and app_id in ids):
            raise ValueError("App 名称或 ID 重复。")
        names.add(app["name"])
        if app_id is not None:
            ids.add(app_id)
    network = config["network"]
    if not 3 <= network["request_interval_seconds"] <= 60:
        raise ValueError("请求间隔必须为 3–60 秒。")
    if network["retries"] != 2:
        raise ValueError("M1 固定失败重试 2 次。")
    llm = config["llm"]
    for value in (network["timeout_seconds"], llm["timeout_seconds"],
                  llm["max_tokens"], llm["max_input_chars"]):
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError("超时和输入输出上限必须为正数。")
    if not isinstance(llm["model"], str) or not llm["model"].strip():
        raise ValueError("缺少模型名称。")
    url = urlsplit(llm["base_url"])
    if url.scheme != "https" or not url.netloc or url.username or url.password or url.query or url.fragment:
        raise ValueError("模型地址必须为不含凭据或查询参数的 HTTPS 地址。")
    return config
