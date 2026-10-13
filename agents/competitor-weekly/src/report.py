import re
from datetime import date


def week_label(day: str) -> str:
    iso = date.fromisoformat(day).isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def plain(value) -> str:
    text = str(value).replace("\n", " ").replace("\r", " ")
    return re.sub(r"([\\`*_{}\[\]<>#|])", r"\\\1", text)


def number(value) -> str:
    return "未提供" if value is None else str(value)


def quoted_original(text: str) -> str:
    # Use a longer fence than any run inside the external text.
    longest = max((len(run) for run in re.findall(r"`+", text)), default=0)
    fence = "`" * max(3, longest + 1)
    return f"{fence}text\n{text}\n{fence}"


def render(current: dict, previous: dict | None, changes: list[dict], summary: dict) -> str:
    active = [change for change in changes if change["status"] != "unchanged"]
    if not active:
        return "本周无重要变化\n"
    lines = [f"# 竞品周报 · {week_label(current['date'])}", ""]
    if current.get("synthetic"):
        lines += ["> 离线演示：以下为虚构测试数据，不代表任何真实 App 的版本、功能或评分。", ""]
    if previous is None:
        headline = f"首周基线：首次记录 {len(changes)} 款 App 的当前版本和评分，尚不能判断本周发生了什么变化。"
    elif summary["headline"]:
        names = {change["app"]["app_id"]: change["app"]["name"] for change in changes}
        headline = f"{names[summary['highlight_app_id']]}：{summary['headline']}（AI 依据更新说明归纳）"
    else:
        versions = sum("version" in change["fields"] for change in changes)
        ratings = sum(bool({"rating", "rating_count"} & set(change["fields"])) for change in changes)
        added = sum(change["status"] == "baseline" for change in changes)
        headline = f"与上一份有效快照相比，{len(active)} 款 App 有变化或新增记录；{versions} 款版本变化，{ratings} 款评分或评分人数变化，{added} 款首次记录。"
    lines += [f"**本周一句话：** {plain(headline)}", ""]
    lines += [f"- 采集时间：{plain(current['observed_at'])}；中国区 App Store"]
    if previous:
        lines += [f"- 实际对比日期：{previous['date']} → {current['date']}（上一份有效快照，并非固定间隔七天）"]
    else:
        lines += ["- 对比日期：无历史快照，本期仅建立基线"]
    if summary["reason"]:
        lines += [f"- 解读状态：{plain(summary['reason'])}"]
    elif summary.get("headline_evidence"):
        lines += [f"- 一句话判断的原文依据：{plain(summary['headline_evidence'])}"]
    for change in active:
        app, before = change["app"], change["before"]
        lines += ["", f"## {plain(app['name'])}" + (" · 首次记录" if before is None else ""), ""]
        version = app["version"] if before is None else f"{before['version']} → {app['version']}"
        rating = number(app["rating"]) if before is None else f"{number(before['rating'])} → {number(app['rating'])}"
        count = number(app["rating_count"]) if before is None else f"{number(before['rating_count'])} → {number(app['rating_count'])}"
        source_label = "演示链接（非真实 App Store）" if current.get("synthetic") else "中国区 App Store"
        lines += [f"- 版本：{plain(version)}", f"- 当前版本更新日期：{plain(app['release_date'] or '未提供')}",
                  f"- 评分（满分 5 分）：{plain(rating)}；评分人数：{plain(count)}",
                  f"- 来源：[{source_label}]({app['url']})", "", "**新功能要点：**", ""]
        points = summary["items"].get(app["app_id"])
        if points:
            for point in points:
                lines += [f"- {plain(point['text'])}（AI 归纳；原文依据：{plain(point['evidence'])}）"]
        elif before is None:
            lines += ["首周仅记录当前版本的更新说明，不将它解释为本周新增功能。"]
        elif not app["release_notes"].strip():
            lines += ["商店未提供更新说明，无法判断具体新功能。"]
        elif not change["notes_changed"]:
            lines += ["更新说明未变化，不推断新增功能。"]
        else:
            lines += ["本次未生成 AI 归纳，请直接查看下方更新说明原文。"]
        lines += ["", "**更新说明原文：**", "", quoted_original(app["release_notes"] or "商店未提供更新说明。")]
    unchanged = [change["app"]["name"] for change in changes if change["status"] == "unchanged"]
    if unchanged:
        lines += ["", "无变化：" + "、".join(plain(name) for name in unchanged) + "。"]
    return "\n".join(lines) + "\n"
