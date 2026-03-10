class SessionState:
    def __init__(self):
        self.intent = None
        self.delivery_type = None
        self.district = None
        self.delivery_fee = 0

        self.items = []
        self.subtotal = 0

    def add_item(self, item, quantity=1):
        # merge if already exists
        for row in self.items:
            if row["id"] == item["id"]:
                row["quantity"] += quantity
                self.subtotal += item["price"] * quantity
                return

        self.items.append({
            "id": item["id"],
            "name_ar": item["name_ar"],
            "price": item["price"],
            "quantity": quantity,
        })
        self.subtotal += item["price"] * quantity

    def remove_item(self, item_name):
        kept = []
        for row in self.items:
            if row["name_ar"] == item_name:
                self.subtotal -= row["price"] * row["quantity"]
            else:
                kept.append(row)
        self.items = kept

    def update_quantity(self, item_name, quantity):
        for row in self.items:
            if row["name_ar"] == item_name:
                self.subtotal -= row["price"] * row["quantity"]
                row["quantity"] = quantity
                self.subtotal += row["price"] * row["quantity"]
                return