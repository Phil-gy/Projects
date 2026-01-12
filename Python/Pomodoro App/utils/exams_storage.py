import json


def load_exams(settings):
    raw = settings.value("exams_json", "")
    if not raw:
        return []

    try:
        data = json.loads(raw)
        out = []
        for item in data:
            if isinstance(item, dict) and "name" in item and "date" in item:
                out.append(item)
        return out
    except Exception:
        return []


def save_exams(settings, exams):
    settings.setValue("exams_json", json.dumps(exams, ensure_ascii=False))
