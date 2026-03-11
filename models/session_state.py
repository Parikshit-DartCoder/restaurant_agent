class SessionState:

    def __init__(self):

        # main cart storage
        self.cart = []

        # compatibility alias (some parts of system expect state.items)
        self.items = self.cart

        # location
        self.district = None
        self.location_confirmed = False

    # -----------------------------------
    # ADD ITEM
    # -----------------------------------

    def add_item(self, item, quantity):

        for cart_item in self.cart:

            if cart_item["id"] == item["id"]:
                cart_item["quantity"] += quantity
                return

        self.cart.append({
            "id": item.get("id", item["name_ar"]),
            "name_ar": item["name_ar"],
            "price": item["price"],
            "quantity": quantity
        })

    # -----------------------------------
    # REMOVE ITEM
    # -----------------------------------

    def remove_item(self, item):

        for cart_item in self.cart:

            if cart_item["id"] == item["id"]:
                self.cart.remove(cart_item)
                return True

        return False

    # -----------------------------------
    # UPDATE ITEM QUANTITY
    # -----------------------------------

    def update_item(self, item, quantity):

        for cart_item in self.cart:

            if cart_item["id"] == item["id"]:
                cart_item["quantity"] = quantity
                return True

        return False

    # -----------------------------------
    # SUBTOTAL
    # -----------------------------------

    def subtotal(self):

        total = 0

        for item in self.cart:
            total += item["price"] * item["quantity"]

        return total

    # -----------------------------------
    # CLEAR CART
    # -----------------------------------

    def clear(self):
        self.cart.clear()