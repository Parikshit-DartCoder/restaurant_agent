from agents.greeting_agent import GreetingAgent
from agents.location_agent import LocationAgent
from agents.order_agent import OrderAgent
from agents.checkout_agent import CheckoutAgent
from agents.escalation_agent import EscalationAgent
from models.session_state import SessionState
from utils.logger import get_logger

logger = get_logger()


def main():

    state = SessionState()

    greeting = GreetingAgent()
    location = LocationAgent()
    order = OrderAgent()
    checkout = CheckoutAgent()
    escalation = EscalationAgent()

    logger.info("Agent system started")

    msg = input("User: ")

    next_step = greeting.run(msg, state)

    if next_step == "ESCALATION":

        print(escalation.run(msg, state))
        return

    logger.info("HANDOFF greeting → location")

    district = input("أدخل الحي: ")

    valid = location.run(district, state)

    if not valid:
        print("لا نوصل لهذه المنطقة")
        return

    while True:

        query = input("ماذا تريد أن تطلب؟ ")

        if query == "خلصت":
            break

        order.run(query, state)

    print(checkout.run(state))


if __name__ == "__main__":
    main()