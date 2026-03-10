from utils.arabic_text import normalize_menu_text, score_text_match


def add_to_order(state, item, quantity=1):
    state.add_item(item, quantity)
    return {
        "status": "added",
        "item": item["name_ar"],
        "quantity": quantity
    }


def get_current_order(state):
    return {
        "items": state.items,
        "subtotal": state.subtotal
    }


def _row_name(row):
    if isinstance(row, dict):
        if "name_ar" in row:
            return row["name_ar"]

        if "item" in row:
            if isinstance(row["item"], dict):
                return row["item"].get("name_ar", "")
            return str(row["item"])

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

    return best_name if best_score >= 50 else None


def render_order_lines(state):
    lines = []
    for row in getattr(state, "items", []):
        lines.append(f"- {_row_name(row)} × {_row_quantity(row)}")
    return lines