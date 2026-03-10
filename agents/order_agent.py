class OrderAgent:

    def run(self, message, state):

        # remove item
        if "شيل" in message:
            item = message.replace("شيل", "").strip()
            state.remove_item(item)
            print(f"تم حذف {item}")
            return

        # update quantity
        if "خلّي" in message:
            parts = message.split()
            item = parts[1]
            qty = int(parts[2])
            state.update_quantity(item, qty)
            print("تم تعديل الكمية")
            return

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message}
        ]

        query = chat(messages)

        items = search_menu(query)

        if not items:
            print("هذا الصنف غير موجود")
            return

        item = items[0]

        state.add_item(item)

        print(f"تمت إضافة {item['name_ar']}")