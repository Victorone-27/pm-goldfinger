FIELDS = ("version", "release_notes", "release_date", "rating", "rating_count")


def compare(current: dict, previous: dict | None) -> list[dict]:
    before_by_id = {app["app_id"]: app for app in previous["apps"]} if previous else {}
    changes = []
    for app in current["apps"]:
        before = before_by_id.get(app["app_id"])
        fields = [key for key in FIELDS if before is not None and app.get(key) != before.get(key)]
        changes.append({
            "app": app, "before": before, "fields": fields,
            "status": "baseline" if before is None else "changed" if fields else "unchanged",
            "notes_changed": before is not None and "release_notes" in fields and bool(app.get("release_notes", "").strip()),
        })
    return changes
