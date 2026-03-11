from utils.arabic_text import normalize_menu_text, score_text_match


def get_current_order(state):

    subtotal = 0

    for item in getattr(state, "items", []):
        subtotal += item["price"] * item["quantity"]

    return {
        "items": state.items,
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

    query = normalize_menu_text(query)

    best_name = None
    best_score = 0

    for row in getattr(state, "items", []):

        name = _row_name(row)

        score = score_text_match(query, name)

        if score > best_score:
            best_score = score
            best_name = name

    if best_score >= 40:
        return best_name

    return None


def render_order_lines(state):

    lines = []

    for row in getattr(state, "items", []):

        name = _row_name(row)
        qty = _row_quantity(row)

        lines.append(f"- {name} × {qty}")

    return lines