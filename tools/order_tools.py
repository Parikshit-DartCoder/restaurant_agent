from services.llm_service import chat_json
from utils.arabic_text import normalize_menu_text, score_text_match


def get_current_order(state):

    subtotal = 0

    for item in getattr(state, "items", []):
        subtotal += item["price"] * item["quantity"]

    return {
        "items": getattr(state, "items", []),
        "subtotal": subtotal
    }


def _row_name(row):

    if isinstance(row, dict):

        if "name_ar" in row:
            return row["name_ar"]

        if "item_name" in row:
            return row["item_name"]

    return str(row)


def _row_quantity(row):

    if isinstance(row, dict):
        return row.get("quantity", 1)

    return 1


def find_best_cart_item(state, query):

    if not query:
        return None

    query_norm = normalize_menu_text(query)

    items = getattr(state, "items", [])

    if not items:
        return None

    names = []

    for row in items:

        name = _row_name(row)

        if name:
            names.append(name)

    if not names:
        return None

    # --------------------------------
    # FAST HEURISTIC MATCH
    # --------------------------------

    best_name = None
    best_score = 0

    for name in names:

        name_norm = normalize_menu_text(name)

        # substring shortcut
        if query_norm in name_norm or name_norm in query_norm:
            return name

        score = score_text_match(query_norm, name_norm)

        if score > best_score:
            best_score = score
            best_name = name

    # heuristic confidence
    if best_score >= 45:
        return best_name

    # --------------------------------
    # LLM FALLBACK
    # --------------------------------

    try:

        result = chat_json([
            {
                "role": "system",
                "content": """
اختر العنصر الأقرب من الطلب الحالي لرسالة المستخدم.

ارجع JSON فقط:

{
 "match": "string أو null"
}

القواعد:
- يجب أن يكون الاختيار من القائمة فقط
- لا تختر عنصر غير موجود
- اذا لا يوجد تطابق جيد ارجع null
"""
            },
            {
                "role": "user",
                "content": f"""
رسالة المستخدم:
{query}

العناصر في الطلب:
{names}
"""
            }
        ])

        match = result.get("match")

        if match in names:
            return match

    except Exception:
        pass

    return None


def render_order_lines(state):

    lines = []

    for row in getattr(state, "items", []):

        name = _row_name(row)
        qty = _row_quantity(row)

        lines.append(f"- {name} × {qty}")

    return lines