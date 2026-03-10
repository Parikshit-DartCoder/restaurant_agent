from tools.order_tools import get_current_order, render_order_lines
from utils.logger import get_logger

logger = get_logger()


class CheckoutAgent:

    def run(self, state):
        logger.info("CHECKOUT started")

        current = get_current_order(state)
        items = current["items"]
        subtotal = current["subtotal"]
        delivery_fee = getattr(state, "delivery_fee", 0)
        total = subtotal + delivery_fee

        if not items:
            response = "الطلب الحالي فارغ."
            print(response)
            return response

        lines = render_order_lines(state)

        response = "\n".join(
            [
                "ملخص الطلب:",
                *lines,
                f"المجموع الفرعي: {subtotal}",
                f"رسوم التوصيل: {delivery_fee}",
                f"الإجمالي: {total}",
            ]
        )

        print(response)
        return response