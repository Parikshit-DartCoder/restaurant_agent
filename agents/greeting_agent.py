from services.llm_service import chat
from utils.logger import get_logger

logger = get_logger("restaurant_agent")

GREETING_WORDS = [
    "hi", "hello", "hey",
    "مرحبا", "اهلا", "السلام", "السلام عليكم"
]

SYSTEM_PROMPT = """
أنت مساعد مطعم.

حدد نية المستخدم.

الخيارات:

GREETING → إذا كان المستخدم يقول مرحبا أو يبدأ المحادثة
ORDER → إذا كان يريد طلب طعام
ESCALATION → إذا كان لديه شكوى أو مشكلة

أجب بكلمة واحدة فقط:

GREETING
ORDER
ESCALATION
"""


class GreetingAgent:

    def run(self, message, state):

        logger.info("AGENT_TRIGGER GreetingAgent")

        msg = (message or "").strip().lower()

        if msg in GREETING_WORDS:

            logger.info("GREETING detected via rule")
            logger.info("HANDOFF GreetingAgent → LocationAgent")

            return "LOCATION"

        result = chat([
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message}
        ]).strip().upper()

        logger.info(f"LLM intent result={result}")

        if result == "ESCALATION":
            state.intent = "complaint"
            logger.info("HANDOFF GreetingAgent → EscalationAgent")
            return "ESCALATION"

        if result == "GREETING":
            logger.info("HANDOFF GreetingAgent → LocationAgent")
            return "LOCATION"

        state.intent = "delivery_order"

        logger.info("HANDOFF GreetingAgent → LocationAgent")

        return "LOCATION"