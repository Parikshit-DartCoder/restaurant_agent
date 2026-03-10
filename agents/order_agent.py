from services.llm_service import chat
from tools.menu_tools import get_best_menu_match, search_menu
from utils.arabic_text import extract_item_hint, extract_quantity, parse_order_edit
from utils.logger import get_logger

logger = get_logger()

SYSTEM_PROMPT = """
أنت مساعد لتحويل طلبات المستخدم إلى اسم صنف عربي قصير من قائمة مطعم.
قد يكتب المستخدم بالعربية أو الإنجليزية أو لهجة أو Arabizi.

أمثلة:
- abgha burger -> برجر
- add fries -> بطاطس
- coke -> كولا
- chicken burger -> برجر دجاج
- shil coke -> كولا
- khalli burger 2 -> برجر

أجب فقط باسم الصنف بالعربية بدون أي شرح.
"""


class OrderAgent:

    def run(self, message, state):
        logger.info(f"ORDER raw message: {message}")

        # 1) Handle edits first: remove / update qty
        edit = parse_order_edit(message)
        if edit:
            matched_item = get_best_menu_match(edit["item_name"])
            item_name = matched_item["name_ar"] if matched_item else edit["item_name"]

            if edit["action"] == "remove":
                state.remove_item(item_name)
                print(f"تم حذف {item_name}")
                return

            if edit["action"] == "update_qty":
                state.update_quantity(item_name, edit["quantity"])
                print(f"تم تعديل كمية {item_name} إلى {edit['quantity']}")
                return

        # 2) Normal add flow
        item_hint = extract_item_hint(message)
        qty = extract_quantity(message, default=1)

        items = search_menu(item_hint)

        # 3) LLM fallback only if local matching failed
        if not items:
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"النص الأصلي: {message}\nالاسم المستخرج: {item_hint}"
                }
            ]
            query = chat(messages)
            items = search_menu(query)

        if not items:
            print("هذا الصنف غير موجود")
            return

        item = items[0]
        state.add_item(item, qty)

        print(f"تمت إضافة {item['name_ar']} × {qty}")