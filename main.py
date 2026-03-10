from agents.checkout_agent import CheckoutAgent
from agents.escalation_agent import EscalationAgent
from agents.greeting_agent import GreetingAgent
from agents.location_agent import LocationAgent
from agents.order_agent import OrderAgent
from models.session_state import SessionState
from utils.arabic_text import parse_confirmation


def main():
    state = SessionState()

    greeting = GreetingAgent()
    escalation = EscalationAgent()
    location = LocationAgent()
    order = OrderAgent()
    checkout = CheckoutAgent()

    first_message = input("User: ").strip()

    next_stage = greeting.run(first_message, state)

    if next_stage == "ESCALATION":
        print(escalation.run(first_message, state))
        return

    district = input("أدخل الحي: ").strip()
    while not location.run(district, state):
        district = input("لا نوصل لهذه المنطقة. أدخل الحي: ").strip()

    while True:
        query = input("ماذا تريد أن تطلب؟ ").strip()

        next_stage = order.run(query, state)

        if next_stage == "CHECKOUT":
            checkout.run(state)

            confirm = input("هل تؤكد الطلب؟ ").strip()
            answer = parse_confirmation(confirm)

            if answer is True:
                print("تم تأكيد الطلب.")
            elif answer is False:
                print("تم إلغاء الطلب.")
            else:
                print("لم أفهم الرد. لم يتم تأكيد الطلب.")
            break


if __name__ == "__main__":
    main()