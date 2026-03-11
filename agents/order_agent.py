from services.llm_service import chat_json
from tools.menu_tools import get_best_menu_match
from utils.arabic_text import normalize_menu_text, contains_any, YES_WORDS
from utils.logger import get_logger

logger = get_logger("restaurant_agent")


class OrderAgent:

    def run(self, message, state):

        logger.info("AGENT_TRIGGER OrderAgent")

        if not message:
            return "لم أفهم الطلب. ماذا تريد أن تطلب؟"

        message = message.strip()

        # ------------------------------------
        # Ignore confirmations
        # ------------------------------------
        if contains_any(message, YES_WORDS):
            return "ماذا تريد أن تطلب؟"

        parsed = None

        try:

            logger.info("LLM_CALL OrderParser")

            parsed = chat_json([
                {
                    "role": "system",
                    "content": """
أنت مساعد طلبات مطعم.

حلل رسالة المستخدم وارجع JSON فقط.

يمكن أن يكون الرد:
object واحد
او list من objects

كل object يجب أن يكون بالشكل التالي:

{
 "action": "add|remove|update|checkout",
 "item": "string",
 "quantity": number
}

قواعد:
- اذا المستخدم يريد انهاء الطلب استخدم action=checkout
- اذا لم يذكر الكمية اجعلها 1
- اذا كان الطلب تعديل كمية استخدم update
- اذا كان حذف استخدم remove
"""
                },
                {"role": "user", "content": message}
            ])

        except Exception as e:

            logger.warning("LLM parsing failed: %s", e)

            return "لم أفهم الطلب. ماذا تريد أن تطلب؟"

        if not parsed:
            return "لم أفهم الطلب. ماذا تريد أن تطلب؟"

        # ------------------------------------
        # Normalize output to list
        # ------------------------------------
        if isinstance(parsed, dict):
            parsed = [parsed]

        responses = []

        for cmd in parsed:

            action = cmd.get("action")
            item = cmd.get("item")
            qty = cmd.get("quantity", 1)

            # ---------------------------
            # CHECKOUT
            # ---------------------------
            if action == "checkout":

                logger.info("HANDOFF OrderAgent → CheckoutAgent")

                return "CHECKOUT"

            if not item:
                continue

            item = normalize_menu_text(item)

            menu_item = get_best_menu_match(item)

            if not menu_item:

                responses.append("عذراً هذا الصنف غير موجود.")

                continue

            # ---------------------------
            # ADD
            # ---------------------------
            if action == "add":

                state.add_item(menu_item, qty)

                logger.info(
                    f"ORDER_ADD {menu_item['name_ar']} x{qty}"
                )

                responses.append(
                    f"تمت إضافة {menu_item['name_ar']} × {qty}"
                )

            # ---------------------------
            # REMOVE
            # ---------------------------
            elif action == "remove":

                if state.remove_item(menu_item):

                    logger.info(
                        f"ORDER_REMOVE {menu_item['name_ar']}"
                    )

                    responses.append(
                        f"تم حذف {menu_item['name_ar']}"
                    )

                else:

                    responses.append(
                        "العنصر غير موجود في الطلب"
                    )

            # ---------------------------
            # UPDATE
            # ---------------------------
            elif action == "update":

                if state.update_item(menu_item, qty):

                    logger.info(
                        f"ORDER_UPDATE {menu_item['name_ar']} x{qty}"
                    )

                    responses.append(
                        f"تم تعديل كمية {menu_item['name_ar']} إلى {qty}"
                    )

                else:

                    responses.append(
                        "العنصر غير موجود في الطلب"
                    )

        if not responses:

            return "لم أفهم الطلب. ماذا تريد أن تطلب؟"

        return "\n".join(responses)