from utils.arabic_text import normalize_arabic
import json
import config

def load_menu():

    with open(config.MENU_PATH, encoding="utf-8") as f:
        return json.load(f)

MENU = load_menu()

def search_menu(query):

    query = normalize_arabic(query)

    results = []

    for item in MENU:

        name = normalize_arabic(item["name_ar"])

        if query in name:
            results.append(item)

    return results[:5]