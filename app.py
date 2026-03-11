import streamlit as st

from agents.checkout_agent import CheckoutAgent
from agents.escalation_agent import EscalationAgent
from agents.greeting_agent import GreetingAgent
from agents.location_agent import LocationAgent
from agents.order_agent import OrderAgent

from models.session_state import SessionState
from utils.logger import get_logger
from utils.arabic_text import normalize_text, contains_any, YES_WORDS

logger = get_logger("router")

st.set_page_config(page_title="Restaurant Agent", layout="centered")
st.title("مساعد طلبات المطعم")

# ---------------- SESSION INIT ----------------

if "state" not in st.session_state:
    st.session_state.state = SessionState()

if "stage" not in st.session_state:
    st.session_state.stage = "GREETING"

if "messages" not in st.session_state:
    st.session_state.messages = []

state = st.session_state.state

# ---------------- AGENTS ----------------

greeting = GreetingAgent()
location = LocationAgent()
order = OrderAgent()
checkout = CheckoutAgent()
escalation = EscalationAgent()

# ---------------- DISPLAY HISTORY ----------------

for role, msg in st.session_state.messages:

    if role == "user":
        st.chat_message("user").write(msg)

    else:
        st.chat_message("assistant").write(msg)

# ---------------- INPUT ----------------

user_input = st.chat_input("اكتب رسالتك")

if not user_input:
    st.stop()

logger.info(f"USER_MESSAGE {user_input}")

st.session_state.messages.append(("user", user_input))

msg = normalize_text(user_input)
stage = st.session_state.stage

logger.info(f"AGENT_TRIGGER {stage}")

reply = None

# ---------------- GREETING ----------------

if stage == "GREETING":

    next_stage = greeting.run(msg, state)

    if next_stage == "ESCALATION":

        logger.info("HANDOFF GREETING → ESCALATION")
        reply = escalation.run(msg, state)

    else:

        logger.info("HANDOFF GREETING → LOCATION")

        st.session_state.stage = "LOCATION"
        reply = "أدخل الحي:"

# ---------------- LOCATION ----------------

elif stage == "LOCATION":

    reply = location.run(msg, state)

    if state.location_confirmed:

        logger.info("HANDOFF LOCATION → ORDER")

        st.session_state.stage = "ORDER"
        reply = f"{reply}\n\nماذا تريد أن تطلب؟"

# ---------------- ORDER ----------------

elif stage == "ORDER":

    result = order.run(msg, state)

    if result == "CHECKOUT":

        if not state.items:

            reply = "الطلب الحالي فارغ."

        else:

            logger.info("HANDOFF ORDER → CHECKOUT")

            summary = checkout.run(state)

            st.session_state.stage = "CONFIRM"
            reply = summary

    else:

        reply = result

# ---------------- CONFIRM ----------------

elif stage == "CONFIRM":

    if contains_any(msg, YES_WORDS):

        logger.info("HANDOFF CHECKOUT → END")

        reply = "تم استلام الطلب. شكراً لك!"

        st.session_state.state = SessionState()
        st.session_state.stage = "GREETING"

    elif any(x in msg for x in ["add", "remove", "change", "update", "غير"]):

        logger.info("HANDOFF CONFIRM → ORDER_EDIT")

        st.session_state.stage = "ORDER"

        result = order.run(msg, state)
        reply = result

    else:

        reply = "هل تؤكد الطلب؟ (نعم / تعديل)"

# ---------------- RESPONSE ----------------

if reply:
    st.session_state.messages.append(("assistant", reply))

st.rerun()