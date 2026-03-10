import json
import config

from utils.arabic_text import normalize_menu_text, normalize_text, score_text_match


def load_menu():
    with open(config.MENU_PATH, encoding="utf-8") as f:
        return json.load(f)


MENU = load_menu()


def _candidate_names(item):
    names = []

    if item.get("name_ar"):
        names.append(normalize_menu_text(item["name_ar"]))

    if item.get("name_en"):
        names.append(normalize_menu_text(item["name_en"]))

    return [n for n in names if n]


def _score_match(query: str, item: dict) -> int:
    query = normalize_menu_text(query)
    if not query:
        return 0

    best = 0
    for name in _candidate_names(item):
        best = max(best, score_text_match(query, name))
    return best


def search_menu(query, limit=5):
    query = normalize_menu_text(query)
    if not query:
        return []

    scored = []
    for item in MENU:
        score = _score_match(query, item)
        if score > 0:
            scored.append((score, item))

    scored.sort(key=lambda x: (-x[0], normalize_text(x[1].get("name_ar", ""))))
    return [item for _, item in scored[:limit]]


def get_best_menu_match(query):
    results = search_menu(query, limit=1)
    return results[0] if results else None