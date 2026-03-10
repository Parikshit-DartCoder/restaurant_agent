from services.llm_service import chat
from utils.arabic_text import detect_intent_hint, normalize_text
from utils.logger import get_logger

logger = get_logger()

SYSTEM_PROMPT = """
أنت مصنف نية لمساعد طلبات مطعم في السعودية.

قد يكتب المستخدم بالعربية أو الإنجليزية أو لهجة خليجية/سعودية أو نص مختلط
أو Arabizi مثل:
- abgha burger
- ابي اطلب
- I want food
- عندي شكوى
- delivery late
- order wrong

القواعد:
- إذا كان يريد طلب طعام أو بدء طلب → ORDER
- إذا كانت شكوى أو مشكلة أو تأخير أو خطأ في الطلب → ESCALATION

أجب فقط بكلمة واحدة:
ORDER
ESCALATION
"""


class GreetingAgent:

    def run(self, message, state):
        hint = detect_intent_hint(message)

        if hint == "ESCALATION":
            state.intent = "complaint"
            return "ESCALATION"

        if hint == "ORDER":
            state.intent = "delivery_order"
            return "LOCATION"

        normalized = normalize_text(message)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"النص الأصلي: {message}\nالنص بعد التطبيع: {normalized}"
            }
        ]

        result = (chat(messages) or "").strip().upper()

        logger.info(f"Greeting LLM result: {result}")

        if "ESCALATION" in result:
            state.intent = "complaint"
            return "ESCALATION"

        state.intent = "delivery_order"
        return "LOCATION"