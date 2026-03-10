import re
from typing import Optional

ARABIC_DIACRITICS = re.compile(
    r"""
    ّ|َ|ً|ُ|ٌ|ِ|ٍ|ْ|ـ
    """,
    re.VERBOSE,
)

MULTISPACE_RE = re.compile(r"\s+")
PUNCT_RE = re.compile(r"""[،,:;!?؟./\\()+\-_*=~"'`[\]{}<>|]+""")
ARABIC_DIGIT_TRANS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")

DISTRICT_ALIASES = {
    "النرجس": [
        "النرجس", "حي النرجس", "narjis", "nargis", "al narjis", "alnarjis", "annarjis"
    ],
    "العقيق": [
        "العقيق", "حي العقيق", "aqiq", "aqeeq", "akeeq", "al aqiq", "alaqiq"
    ],
    "الملقا": [
        "الملقا", "حي الملقا", "malqa", "malga", "al malqa", "almalqa"
    ],
}

MENU_ALIASES = {
    "برجر": ["burger", "burgar", "burgr", "برغر", "برجر"],
    "برجر لحم": ["beef burger", "burger beef", "برجر لحم", "لحم burger"],
    "برجر دجاج": ["chicken burger", "burger chicken", "برجر دجاج"],
    "برجر دجاج سبايسي": ["spicy chicken burger", "spicy burger", "spicy chicken", "سبايسي برجر"],
    "بطاطس": ["fries", "french fries", "chips", "بطاطس"],
    "كولا": ["cola", "coke", "كوكاكولا", "كوك", "كولا"],
    "بيبسي": ["pepsi", "بيبسي"],
    "زنجر": ["zinger", "زنجر"],
    "شاورما": ["shawarma", "shawerma", "shawrma", "شاورما"],
    "بروست": ["broast", "broasted", "بروست"],
    "وجبه": ["meal", "combo", "وجبة", "وجبه"],
    "جبنه": ["cheese", "جبن", "جبنة", "جبنه"],
    "دجاج": ["chicken", "دجاج"],
    "لحم": ["beef", "meat", "لحم"],
    "ماء": ["water", "موية", "مويه", "ماي", "ماء"],
    "عصير": ["juice", "jus", "عصير"],
    "سلطه": ["salad", "salata", "سلطة", "سلطه"],
}

ORDER_WORDS = {
    "order", "طلب", "اطلب", "ابي", "أبي", "abii", "abgha", "abga", "abgy", "ابغى", "أبغى",
    "عايز", "عاوزه", "اريد", "أريد", "ودي", "hungry", "food", "meal", "burger", "shawarma", "broast"
}

COMPLAINT_WORDS = {
    "complaint", "problem", "issue", "wrong", "late", "delay", "bad", "refund", "cancel order",
    "شكوى", "مشكله", "مشكلة", "خطا", "خطأ", "متاخر", "متأخر", "تاخير", "تأخير", "بارد", "سيئ", "سيء"
}

REMOVE_WORDS = {
    "شيل", "احذف", "الغ", "الغي", "remove", "delete", "cancel", "shil", "sheel", "erase"
}

UPDATE_WORDS = {
    "خلي", "خل", "خله", "خلها", "خلّي", "غير", "بدل",
    "change", "update", "make it", "khalli", "khali", "khali"
}

ADD_WORDS = {
    "add", "plus", "ابي", "ابغى", "أبي", "أبغى", "اريد", "أريد", "عايز", "عاوزه", "ضيف", "اضف", "أضف"
}

CHECKOUT_WORDS = {
    "checkout", "check out", "done", "finish", "finalize", "confirm order",
    "يلا تشيك اوت", "تشيك اوت", "انهاء", "انه الطلب", "خلص", "خلاص", "تمام خلص",
    "ابي اكد", "ابغى اكد", "تاكيد الطلب", "أكد الطلب", "اكمل", "كمل"
}

FILLER_WORDS = {
    "ابي", "ابغى", "أبي", "أبغى", "اريد", "أريد", "عايز", "عاوزه", "لو", "سمحت", "please",
    "ممكن", "ضيف", "اضف", "أضف", "add", "order", "طلب", "اطلب", "لي", "ليا",
    "انا", "اني", "في", "the", "a", "an", "bro", "pls", "please"
}

YES_WORDS = {
    "ايوه", "اي", "أيوه", "نعم", "yes", "yep", "ok", "okay", "تمام", "تم", "confirm", "اكيد"
}

NO_WORDS = {
    "لا", "no", "cancel", "وقف", "stop", "مو", "مش", "not now"
}

NUMBER_WORDS = {
    "0": 0, "zero": 0, "صفر": 0,
    "1": 1, "one": 1, "واحد": 1, "واحدة": 1, "wahid": 1, "wa7d": 1,
    "2": 2, "two": 2, "اثنين": 2, "اتنين": 2, "اثنان": 2, "ثنين": 2, "tneen": 2, "ithnain": 2,
    "3": 3, "three": 3, "ثلاثة": 3, "ثلاثه": 3, "تلاتة": 3, "tlata": 3,
    "4": 4, "four": 4, "اربعة": 4, "أربعة": 4, "اربعه": 4, "arba": 4,
    "5": 5, "five": 5, "خمسة": 5, "خمسه": 5, "khamsa": 5,
    "6": 6, "six": 6, "ستة": 6, "سته": 6,
    "7": 7, "seven": 7, "سبعة": 7, "سبعه": 7,
    "8": 8, "eight": 8, "ثمانية": 8, "ثمانيه": 8,
    "9": 9, "nine": 9, "تسعة": 9, "تسعه": 9,
    "10": 10, "ten": 10, "عشرة": 10, "عشره": 10,
}


def remove_diacritics(text: str) -> str:
    return re.sub(ARABIC_DIACRITICS, "", str(text or ""))


def normalize_arabic(text: str) -> str:
    text = remove_diacritics(str(text or ""))
    replacements = {
        "أ": "ا",
        "إ": "ا",
        "آ": "ا",
        "ؤ": "و",
        "ئ": "ي",
        "ة": "ه",
        "ى": "ي",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text


def normalize_text(text: str) -> str:
    text = str(text or "")
    text = text.translate(ARABIC_DIGIT_TRANS)
    text = normalize_arabic(text).lower()
    text = PUNCT_RE.sub(" ", text)
    text = MULTISPACE_RE.sub(" ", text).strip()
    return text


def _phrase_in_text(text: str, phrase: str) -> bool:
    text = f" {normalize_text(text)} "
    phrase = normalize_text(phrase)
    if not phrase:
        return False
    return f" {phrase} " in text or phrase in text


def contains_any(text: str, words) -> bool:
    for word in words:
        if _phrase_in_text(text, word):
            return True
    return False


def replace_aliases(text: str, alias_map: dict) -> str:
    text = normalize_text(text)
    pairs = []
    for canonical, variants in alias_map.items():
        for variant in variants:
            pairs.append((normalize_text(variant), normalize_text(canonical)))
    pairs.sort(key=lambda x: len(x[0]), reverse=True)

    for variant, canonical in pairs:
        if variant:
            text = re.sub(rf"\b{re.escape(variant)}\b", canonical, text)
    return MULTISPACE_RE.sub(" ", text).strip()


def score_text_match(a: str, b: str) -> int:
    a = normalize_menu_text(a)
    b = normalize_menu_text(b)
    if not a or not b:
        return 0
    if a == b:
        return 100
    if a in b or b in a:
        return 80

    a_tokens = set(a.split())
    b_tokens = set(b.split())
    overlap = len(a_tokens & b_tokens)
    if overlap == 0:
        return 0
    return overlap * 25


def canonicalize_district(text: str) -> Optional[str]:
    text = normalize_text(text).replace("حي ", "").strip()

    for canonical, variants in DISTRICT_ALIASES.items():
        for variant in variants:
            v = normalize_text(variant).replace("حي ", "").strip()
            if text == v or f" {v} " in f" {text} " or v in text:
                return canonical

    best_name = None
    best_score = 0
    for canonical in DISTRICT_ALIASES.keys():
        score = score_text_match(text, canonical)
        if score > best_score:
            best_score = score
            best_name = canonical

    return best_name if best_score >= 50 else None


def normalize_menu_text(text: str) -> str:
    return replace_aliases(text, MENU_ALIASES)


def extract_quantity(text: str, default=1):
    text = normalize_text(text)

    m = re.search(r"\b\d+\b", text)
    if m:
        return int(m.group())

    for token in text.split():
        if token in NUMBER_WORDS:
            return NUMBER_WORDS[token]

    return default


def strip_control_words(text: str) -> str:
    text = normalize_menu_text(text)
    removable = set()
    removable |= FILLER_WORDS
    removable |= REMOVE_WORDS
    removable |= UPDATE_WORDS
    removable |= ADD_WORDS
    removable |= CHECKOUT_WORDS

    for word in sorted(removable, key=len, reverse=True):
        w = normalize_text(word)
        if w:
            text = re.sub(rf"\b{re.escape(w)}\b", " ", text)

    text = re.sub(r"\b\d+\b", " ", text)

    for word in sorted(NUMBER_WORDS.keys(), key=len, reverse=True):
        w = normalize_text(word)
        if w:
            text = re.sub(rf"\b{re.escape(w)}\b", " ", text)

    return MULTISPACE_RE.sub(" ", text).strip()


def extract_item_hint(text: str) -> str:
    return strip_control_words(text)


def parse_order_edit(message: str):
    text = normalize_menu_text(message)

    if contains_any(text, REMOVE_WORDS):
        item_name = extract_item_hint(text)
        if item_name:
            return {"action": "remove", "item_name": item_name, "quantity": None}

    if contains_any(text, UPDATE_WORDS):
        item_name = extract_item_hint(text)
        qty = extract_quantity(text, default=None)
        if item_name and qty is not None:
            return {"action": "update_qty", "item_name": item_name, "quantity": qty}

    return None


def detect_intent_hint(message: str):
    text = normalize_text(message)

    if contains_any(text, COMPLAINT_WORDS):
        return "ESCALATION"

    if contains_any(text, ORDER_WORDS):
        return "ORDER"

    return None


def is_checkout_request(message: str) -> bool:
    return contains_any(message, CHECKOUT_WORDS)


def parse_confirmation(message: str):
    text = normalize_text(message)

    if contains_any(text, YES_WORDS):
        return True

    if contains_any(text, NO_WORDS):
        return False

    return None