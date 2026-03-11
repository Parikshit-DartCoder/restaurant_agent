import sys
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from agents.greeting_agent import GreetingAgent
from agents.location_agent import LocationAgent
from agents.order_agent import OrderAgent
from agents.checkout_agent import CheckoutAgent
from agents.escalation_agent import EscalationAgent
from models.session_state import SessionState
from utils.arabic_text import normalize_text, contains_any, YES_WORDS


def simulate_conversation(messages):

    state = SessionState()

    greeting = GreetingAgent()
    location = LocationAgent()
    order = OrderAgent()
    checkout = CheckoutAgent()
    escalation = EscalationAgent()

    stage = "GREETING"

    print("\n==============================")
    print("NEW TEST CONVERSATION")
    print("==============================\n")

    for message in messages:

        msg = normalize_text(message)

        print("USER:", message)

        # GREETING
        if stage == "GREETING":

            next_stage = greeting.run(msg, state)

            if next_stage == "ESCALATION":
                print("BOT:", escalation.run(msg, state))
                return

            print("BOT: أدخل الحي:")
            stage = "LOCATION"
            continue

        # LOCATION
        if stage == "LOCATION":

            reply = location.run(msg, state)
            print("BOT:", reply)

            if state.location_confirmed:
                stage = "ORDER"
                print("BOT: ماذا تريد أن تطلب؟")

            continue

        # ORDER
        if stage == "ORDER":

            result = order.run(msg, state)

            if result == "CHECKOUT":

                if not state.items:
                    print("BOT: الطلب فارغ")
                else:
                    summary = checkout.run(state)
                    print("BOT:", summary)
                    stage = "CONFIRM"

            else:
                print("BOT:", result)

            continue

        # CONFIRM
        if stage == "CONFIRM":

            if contains_any(msg, YES_WORDS):
                print("BOT: تم استلام الطلب. شكراً لك!")
                return

            elif any(x in msg for x in ["add","remove","change","update","غير","شيل"]):
                stage = "ORDER"
                result = order.run(msg, state)
                print("BOT:", result)

            else:
                print("BOT: هل تؤكد الطلب؟ (نعم / تعديل)")


# ---------------------------------------------------
# COMPLEX TEST CASES
# ---------------------------------------------------

tests = [

# ---------------------------------------------------
# SAUDI DETERMINISTIC TESTS
# ---------------------------------------------------

["السلام عليكم","malqa","ايه","ابي برجر وبطاطس وكولا","حساب","نعم"],

["هلا","malqa","ايه","ابي برجر وبطاطس","خل البطاطس 3","خلاص","نعم"],

["مرحبا","malqa","ايه","ابي برجر وبطاطس","غير البطاطس 3","خلص","نعم"],

["هلا","malqa","ايه","ابي برجر وبطاطس وكولا","شيل الكولا","حساب","نعم"],

["هلا","malqa","ايه","ابي برجر وبطاطس وكولا","شيل الكولا","ضيف زنجر","خلاص","نعم"],

["هلا","malqa","ايه","ابي 2 برجر و3 بطاطس","خلص","نعم"],

["هلا","malqa","ايه","ابي زنجر وبطاطس وكولا","تمام","نعم"],

["هلا","malqa","ايه","ابي زنجر وبطاطس وكولا","خل البطاطس 2","حساب","نعم"],

["هلا","malqa","ايه","ضيف بطاطس","شيل بطاطس","خلاص","نعم"],

["هلا","malqa","ايه","ابي برجر","خل البرجر 3","حساب","نعم"],

["هلا","malqa","ايه","ابي برجر وبطاطس وكولا","غير البطاطس 2","شيل الكولا","خلاص","نعم"],

["هلا","malqa","ايه","ابي برجر","حساب","ضيف بطاطس","حساب","نعم"],

["هلا","malqa","ايه","ابي برجر وبطاطس وكولا","شيل البطاطس","ضيف زنجر","غير زنجر 3","حساب","نعم"],

["هلا","malqa","ايه","ابي زنجر وبطاطس","شيل بطاطس","ضيف كولا","خلاص","نعم"],

["هلا","malqa","ايه","ضيف برجر","ضيف بطاطس","شيل برجر","حساب","نعم"],

["هلا","malqa","ايه","ابي برجر","ابي برجر","خل البرجر 3","خلص","نعم"],

["هلا","malqa","ايه","ابي برجر بطاطس كولا","غير البطاطس 3","غير الكولا 2","خلاص","نعم"],

["هلا","malqa","ايه","ابي برجر بطاطس كولا","شيل البطاطس","ضيف زنجر","غير زنجر 3","ضيف بطاطس","حساب","نعم"],

["هلا","malqa","ايه","ابي برجر","ضيف بطاطس","شيل بطاطس","ضيف كولا","شيل كولا","ضيف زنجر","خلاص","نعم"],


# ---------------------------------------------------
# ENGLISH DETERMINISTIC TESTS
# ---------------------------------------------------

["hi","malqa","yes","add burger coke fries","that's it","yes"],

["hi","malqa","yes","add burger fries","change fries to 3","done","yes"],

["hi","malqa","yes","add burger coke fries","remove coke","that's it","yes"],

["hi","malqa","yes","add burger","that's it","add fries","done","yes"],

["hi","malqa","yes","add burger","change burger to three","done","yes"],


# ---------------------------------------------------
# SAUDI LLM FALLBACK TESTS
# ---------------------------------------------------

["هلا","malqa","ايه","ابي شي آكله","خلاص","نعم"],

["هلا","malqa","ايه","فاجئني","حساب","نعم"],

["هلا","malqa","ايه","ابي شي حار","خلاص","نعم"],

["هلا","malqa","ايه","ابي شي رخيص","خلص","نعم"],

["هلا","malqa","ايه","عطني وجبة","حساب","نعم"],

["هلا","malqa","ايه","ابي شي كويس","خلاص","نعم"],

["هلا","malqa","ايه","اطلب لي شي","حساب","نعم"],


# ---------------------------------------------------
# ENGLISH LLM FALLBACK TESTS
# ---------------------------------------------------

["hi","malqa","yes","i want food","that's it","yes"],

["hi","malqa","yes","surprise me","done","yes"],

["hi","malqa","yes","give me something spicy","that's it","yes"],

["hi","malqa","yes","give me something cheap","done","yes"],

["hi","malqa","yes","give me a combo meal","that's it","yes"],

["hi","malqa","yes","i want something good","done","yes"],

["hi","malqa","yes","order for me","that's it","yes"]

]


if __name__ == "__main__":

    for case in tests:
        simulate_conversation(case)