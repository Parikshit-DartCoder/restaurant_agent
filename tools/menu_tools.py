import json
import os
from difflib import get_close_matches

# -------------------------------------------------
# Load menu.json
# -------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MENU_PATH = os.path.join(BASE_DIR, "data", "menu.json")

with open(MENU_PATH, "r", encoding="utf-8") as f:
    MENU = json.load(f)


# -------------------------------------------------
# Build search indexes
# -------------------------------------------------

EN_INDEX = {}
AR_INDEX = {}

for item in MENU:
    EN_INDEX[item["name_en"].lower()] = item
    AR_INDEX[item["name_ar"]] = item


# -------------------------------------------------
# Aliases
# -------------------------------------------------

ALIASES = {
    "coke": "coca-cola",
    "cola": "coca-cola",
    "كوكا": "كوكاكولا",
    "بطاطا": "بطاطس",
}


def normalize(text):

    text = text.lower().strip()

    if text in ALIASES:
        text = ALIASES[text]

    return text


# -------------------------------------------------
# Best menu match
# -------------------------------------------------

def get_best_menu_match(query):

    query = normalize(query)

    # direct english
    if query in EN_INDEX:
        return EN_INDEX[query]

    # direct arabic
    if query in AR_INDEX:
        return AR_INDEX[query]

    # fuzzy english
    en_matches = get_close_matches(query, EN_INDEX.keys(), n=1, cutoff=0.6)

    if en_matches:
        return EN_INDEX[en_matches[0]]

    # fuzzy arabic
    ar_matches = get_close_matches(query, AR_INDEX.keys(), n=1, cutoff=0.6)

    if ar_matches:
        return AR_INDEX[ar_matches[0]]

    return None