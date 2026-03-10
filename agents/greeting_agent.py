from services.llm_service import chat
from utils.logger import get_logger

logger = get_logger()

SYSTEM_PROMPT = """
أنت مساعد طلبات مطعم في السعودية.

مهمتك:
تحديد نية المستخدم.

إذا كان يريد طلب طعام → ORDER
إذا كانت شكوى → ESCALATION

أجب فقط بالكلمة:
ORDER
ESCALATION
"""


class GreetingAgent:

    def run(self, message, state):

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message}
        ]

        result = chat(messages)

        logger.info(f"Greeting LLM result: {result}")

        if "ESCALATION" in result:

            state.intent = "complaint"
            return "ESCALATION"

        state.intent = "delivery_order"
        return "LOCATION"