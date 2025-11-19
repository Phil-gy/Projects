import json
import os, sys

# Always resolve path relative to this file’s location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_PATH = os.path.join(DATA_DIR, "entries.json")

def load_entries():
    """Load all journal entries from file."""
    if not os.path.exists(DATA_PATH):
        return {}
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_entries(entries):
    """Save all journal entries to file."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=4, ensure_ascii=False)

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller .exe"""
    if hasattr(sys, "_MEIPASS"):  # when running from .exe
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)
