import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_PATH = os.path.join(DATA_DIR, "goals.json")

def load_goals():
    if not os.path.exists(DATA_PATH):
        return []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_goals(goals):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(goals, f, indent=4, ensure_ascii=False)
