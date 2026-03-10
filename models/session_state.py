class SessionState:

    def __init__(self):

        self.intent = None
        self.delivery_type = None
        self.district = None
        self.delivery_fee = 0

        self.items = []
        self.subtotal = 0

    def add_item(self, item, quantity=1):

        self.items.append({
            "id": item["id"],
            "name_ar": item["name_ar"],
            "price": item["price"],
            "quantity": quantity
        })

        self.subtotal += item["price"] * quantity