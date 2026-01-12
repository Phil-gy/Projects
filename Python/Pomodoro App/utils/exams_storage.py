import json


def load_exams(settings):
    raw = settings.value("exams_json", "", str)
    if not raw:
        return []

    try:
        data = json.loads(raw)
        out = []
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and "name" in item and "date" in item:
                    out.append({"name": str(item["name"]), "date": str(item["date"])})
        return out
    except Exception:
        return []


def save_exams(settings, exams):
    settings.setValue("exams_json", json.dumps(exams, ensure_ascii=False))
    settings.sync()
