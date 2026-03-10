import re

ARABIC_DIACRITICS = re.compile("""
                             ّ    | # Shadda
                             َ    | # Fatha
                             ً    | # Tanwin Fath
                             ُ    | # Damma
                             ٌ    | # Tanwin Damm
                             ِ    | # Kasra
                             ٍ    | # Tanwin Kasr
                             ْ    | # Sukun
                             ـ
                         """, re.VERBOSE)

def remove_diacritics(text):

    return re.sub(ARABIC_DIACRITICS, '', text)


def normalize_arabic(text):

    text = remove_diacritics(text)

    replacements = {
        "أ": "ا",
        "إ": "ا",
        "آ": "ا",
        "ة": "ه",
        "ى": "ي"
    }

    for k, v in replacements.items():
        text = text.replace(k, v)

    return text