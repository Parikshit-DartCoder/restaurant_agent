import json
import os
from difflib import get_close_matches
from utils.arabic_text import normalize_menu_text

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MENU_PATH = os.path.join(BASE_DIR, "data", "menu.json")

with open(MENU_PATH, "r", encoding="utf-8") as f:
    MENU = json.load(f)

EN_INDEX = {}
AR_INDEX = {}

for item in MENU:

    en = normalize_menu_text(item["name_en"])
    ar = normalize_menu_text(item["name_ar"])

    EN_INDEX[en] = item
    AR_INDEX[ar] = item


def get_best_menu_match(query):

    query = normalize_menu_text(query)

    if query in EN_INDEX:
        return EN_INDEX[query]

    if query in AR_INDEX:
        return AR_INDEX[query]

    en_matches = get_close_matches(query, EN_INDEX.keys(), n=1, cutoff=0.6)

    if en_matches:
        return EN_INDEX[en_matches[0]]

    ar_matches = get_close_matches(query, AR_INDEX.keys(), n=1, cutoff=0.6)

    if ar_matches:
        return AR_INDEX[ar_matches[0]]

    return None