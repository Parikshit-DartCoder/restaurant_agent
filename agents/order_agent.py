from services.llm_service import chat_json
from tools.menu_tools import get_best_menu_match
from tools.order_tools import find_best_cart_item
from utils.arabic_text import normalize_menu_text, contains_any, YES_WORDS
from utils.logger import get_logger

logger = get_logger("restaurant_agent")


class OrderAgent:

    def run(self, message, state):

        logger.info("AGENT_TRIGGER OrderAgent")

        if not message:
            return "لم أفهم الطلب. ماذا تريد أن تطلب؟"

        message = message.strip()

        # ignore confirmations
        if contains_any(message, YES_WORDS):
            return "ماذا تريد أن تطلب؟"

        try:

            parsed = chat_json([
                {
                    "role": "system",
                    "content": """
حلل رسالة المستخدم وارجع JSON فقط.

{
 "action": "add|remove|update|replace|checkout",
 "item": "string أو null",
 "new_item": "string أو null",
 "quantity": number
}

القواعد:
- اذا المستخدم يريد انهاء الطلب استخدم checkout
- اذا لم يذكر الكمية اجعلها 1
- يمكن ارجاع اكثر من امر في قائمة
"""
                },
                {"role": "user", "content": message}
            ])

        except Exception as e:

            logger.warning(f"LLM parsing failed: {e}")

            return "لم أفهم الطلب. ماذا تريد أن تطلب؟"

        if isinstance(parsed, dict):
            parsed = [parsed]

        responses = []

        for cmd in parsed:

            action = cmd.get("action")
            item = cmd.get("item")
            new_item = cmd.get("new_item")
            qty = cmd.get("quantity", 1)

            if action == "checkout":
                return "CHECKOUT"

            if item:
                item = normalize_menu_text(item)

            if new_item:
                new_item = normalize_menu_text(new_item)

            # ---------------- ADD ----------------
            if action == "add":

                if not item:
                    responses.append("ما هو الصنف الذي تريد إضافته؟")
                    continue

                menu_item = get_best_menu_match(item)

                if not menu_item:
                    responses.append("هذا الصنف غير موجود.")
                    continue

                state.add_item(menu_item, qty)

                responses.append(
                    f"تمت إضافة {menu_item['name_ar']} × {qty}"
                )

            # ---------------- REMOVE ----------------
            elif action == "remove":

                cart_name = find_best_cart_item(state, item)

                if cart_name:

                    menu_item = get_best_menu_match(cart_name)

                    if menu_item:
                        state.remove_item(menu_item)
                        responses.append(f"تم حذف {cart_name}")
                    else:
                        responses.append("العنصر غير موجود في الطلب")

                else:
                    responses.append("العنصر غير موجود في الطلب")

            # ---------------- UPDATE ----------------
            elif action == "update":

                cart_name = find_best_cart_item(state, item)

                if cart_name:

                    menu_item = get_best_menu_match(cart_name)

                    if menu_item:
                        state.update_item(menu_item, qty)
                        responses.append(
                            f"تم تعديل كمية {cart_name} إلى {qty}"
                        )
                    else:
                        responses.append("العنصر غير موجود في الطلب")

                else:
                    responses.append("العنصر غير موجود في الطلب")

            # ---------------- REPLACE ----------------
            elif action == "replace":

                old_name = find_best_cart_item(state, item)

                new_menu = get_best_menu_match(new_item)

                if old_name and new_menu:

                    old_menu = get_best_menu_match(old_name)

                    state.remove_item(old_menu)
                    state.add_item(new_menu, qty)

                    responses.append(
                        f"تم حذف {old_menu['name_ar']} وتمت إضافة {new_menu['name_ar']} × {qty}"
                    )

                else:

                    responses.append("تعذر تنفيذ الاستبدال.")

        if not responses:
            return "لم أفهم الطلب."

        return "\n".join(responses)