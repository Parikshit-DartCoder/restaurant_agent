from utils.logger import get_logger

logger = get_logger()

class CheckoutAgent:

    def run(self, state):

        logger.info("CHECKOUT started")

        total = state.subtotal + state.delivery_fee