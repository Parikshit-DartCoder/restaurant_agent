from tools.order_tools import find_best_cart_item


def add_item(state, item, qty):

    for row in state.items:

        if row["name_ar"] == item["name_ar"]:
            row["quantity"] += qty
            return f"تم تحديث {item['name_ar']} × {row['quantity']}"

    state.add_item(item, qty)

    return f"تمت إضافة {item['name_ar']} × {qty}"


def remove_item(state, item_hint):

    cart_name = find_best_cart_item(state, item_hint)

    if not cart_name:
        return "لم أجد هذا الصنف في الطلب"

    state.remove_item(cart_name)

    return f"تم حذف {cart_name}"


def update_quantity(state, item_hint, qty):

    cart_name = find_best_cart_item(state, item_hint)

    if not cart_name:
        return "لم أجد هذا الصنف"

    state.update_quantity(cart_name, qty)

    return f"تم تعديل كمية {cart_name} إلى {qty}"