import re
import json
import os

# ----------------------------------
# BASIC NORMALIZATION
# ----------------------------------

def normalize_text(text: str):

    if not text:
        return ""

    text = text.lower()

    text = text.replace("أ", "ا")
    text = text.replace("إ", "ا")
    text = text.replace("آ", "ا")
    text = text.replace("ة", "ه")
    text = text.replace("ى", "ي")

    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


# ----------------------------------
# BUILD MENU INDEX
# ----------------------------------

_MENU_INDEX = None


def _build_menu_index():

    global _MENU_INDEX

    if _MENU_INDEX:
        return _MENU_INDEX

    base_dir = os.path.dirname(os.path.dirname(__file__))
    menu_path = os.path.join(base_dir, "data", "menu.json")

    with open(menu_path, "r", encoding="utf-8") as f:
        menu = json.load(f)

    index = {}

    for item in menu:

        ar = normalize_text(item["name_ar"])
        en = normalize_text(item["name_en"])

        index[ar] = ar
        index[en] = ar

        for token in ar.split():
            index[token] = ar

        for token in en.split():
            index[token] = ar

    _MENU_INDEX = index

    return index


# ----------------------------------
# MENU NORMALIZER
# ----------------------------------

def normalize_menu_text(text):

    text = normalize_text(text)

    index = _build_menu_index()

    if text in index:
        return index[text]

    tokens = text.split()

    for t in tokens:
        if t in index:
            return index[t]

    return text


# ----------------------------------
# SIMPLE FUZZY SCORE
# ----------------------------------

def score_text_match(a, b):

    a = normalize_text(a)
    b = normalize_text(b)

    if not a or not b:
        return 0

    if a == b:
        return 100

    if a in b or b in a:
        return 80

    tokens_a = set(a.split())
    tokens_b = set(b.split())

    overlap = tokens_a.intersection(tokens_b)

    if overlap:
        return 60

    return 0


# ----------------------------------
# DISTRICT NORMALIZATION
# ----------------------------------

def canonicalize_district(text):

    text = normalize_text(text)

    mapping = {
        "malqa": "الملقا",
        "الملقا": "الملقا",
        "aqiq": "العقيق",
        "العقيق": "العقيق",
        "narjis": "النرجس",
        "النرجس": "النرجس",
    }

    return mapping.get(text)


# ----------------------------------
# CONFIRMATION WORDS
# ----------------------------------

YES_WORDS = {
    "yes",
    "yeah",
    "yep",
    "ok",
    "okay",
    "نعم",
    "اي",
    "ايه",
    "ايوه",
    "تمام"
}

NO_WORDS = {
    "no",
    "لا"
}


def contains_any(text, words):

    text = normalize_text(text)

    for w in words:
        if w in text:
            return True

    return False