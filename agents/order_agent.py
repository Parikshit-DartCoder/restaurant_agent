from services.llm_service import LLMUnavailableError, chat_json
from tools.menu_tools import get_best_menu_match, search_menu
from tools.order_tools import find_best_cart_item
from utils.arabic_text import (
    extract_item_hint,
    extract_quantity,
    is_checkout_request,
    normalize_menu_text,
    parse_order_edit,
)
from utils.logger import get_logger

logger = get_logger()

SYSTEM_PROMPT = """
أنت محلل لرسالة طلب مطعم. قد يكتب المستخدم بالعربية أو الإنجليزية أو لهجة أو Arabizi.

استخرج النية في JSON فقط بالشكل:
{
  "action": "add|remove|update_qty|checkout|unknown",
  "item_name": "<short item hint or empty string>",
  "quantity": <number or null>
}

أمثلة:
"abgha 2 burger" -> {"action":"add","item_name":"burger","quantity":2}
"add fries" -> {"action":"add","item_name":"fries","quantity":1}
"shil fries" -> {"action":"remove","item_name":"fries","quantity":null}
"khalli burger 3" -> {"action":"update_qty","item_name":"burger","quantity":3}
"yalla checkout" -> {"action":"checkout","item_name":"","quantity":null}
"""


class OrderAgent:

    def _apply_edit(self, action, item_hint, qty, state):
        cart_name = find_best_cart_item(state, item_hint)

        if not cart_name:
            menu_match = get_best_menu_match(item_hint)
            if menu_match:
                cart_name = find_best_cart_item(state, menu_match["name_ar"])

        if not cart_name:
            print("لم أجد هذا الصنف في الطلب الحالي")
            return None

        if action == "remove":
            state.remove_item(cart_name)
            print(f"تم حذف {cart_name}")
            return None

        if action == "update_qty":
            if qty is None:
                print("لم أفهم الكمية المطلوبة")
                return None
            state.update_quantity(cart_name, qty)
            print(f"تم تعديل كمية {cart_name} إلى {qty}")
            return None

        return None

    def _apply_add(self, item_hint, qty, state):
        items = search_menu(item_hint)

        if not items:
            return False

        item = items[0]
        state.add_item(item, qty or 1)
        print(f"تمت إضافة {item['name_ar']} × {qty or 1}")
        return True

    def run(self, message, state):
        logger.info(f"ORDER raw message: {message}")

        if is_checkout_request(message):
            return "CHECKOUT"

        local_edit = parse_order_edit(message)
        if local_edit:
            return self._apply_edit(
                local_edit["action"],
                local_edit["item_name"],
                local_edit["quantity"],
                state,
            )

        item_hint = extract_item_hint(message)
        qty = extract_quantity(message, default=1)

        if item_hint and self._apply_add(item_hint, qty, state):
            return None

        try:
            parsed = chat_json(
                [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": f"raw={message}\nlocal_item_hint={item_hint}\nlocal_qty={qty}"
                    }
                ]
            )

            action = (parsed.get("action") or "unknown").strip().lower()
            llm_item_hint = normalize_menu_text(parsed.get("item_name") or item_hint or "")
            llm_qty = parsed.get("quantity", qty)

            if action == "checkout":
                return "CHECKOUT"

            if action in {"remove", "update_qty"}:
                return self._apply_edit(action, llm_item_hint, llm_qty, state)

            if action == "add":
                if self._apply_add(llm_item_hint, llm_qty or 1, state):
                    return None

        except LLMUnavailableError as e:
            logger.warning(f"Order LLM unavailable: {e}")
        except Exception as e:
            logger.warning(f"Order LLM parse failed: {e}")

        print("هذا الصنف غير موجود أو لم أفهم الطلب")
        return None