from tools.order_tools import get_current_order, render_order_lines
from utils.logger import get_logger

logger = get_logger("restaurant_agent")


class CheckoutAgent:

    def run(self, state):

        logger.info("AGENT_TRIGGER CheckoutAgent")

        current = get_current_order(state)

        items = current["items"]
        subtotal = current["subtotal"]
        delivery_fee = getattr(state, "delivery_fee", 0)

        total = subtotal + delivery_fee

        if not items:

            logger.info("CHECKOUT_EMPTY_CART")

            return """الطلب الحالي فارغ.

يمكنك طلب عناصر من القائمة.

أمثلة:
- 2 زنجر
- add fries
"""

        lines = render_order_lines(state)

        logger.info(
            f"CHECKOUT subtotal={subtotal} delivery={delivery_fee} total={total}"
        )

        response = "\n".join(
            [
                "ملخص الطلب:",
                *lines,
                f"المجموع الفرعي: {subtotal}",
                f"رسوم التوصيل: {delivery_fee}",
                f"الإجمالي: {total}",
                "هل تؤكد الطلب؟ (نعم / تعديل)"
            ]
        )

        return response