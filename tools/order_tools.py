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