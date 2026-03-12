from services.llm_service import chat_json
from tools.delivery_tools import check_delivery_district
from utils.logger import get_logger

logger = get_logger("restaurant_agent")

SYSTEM_PROMPT = """
استخرج اسم الحي فقط من رسالة المستخدم.

ارجع JSON:

{
 "district": "string"
}
"""


class LocationAgent:

    def run(self, message, state):

        logger.info("AGENT_TRIGGER LocationAgent")

        # escalation detection
        if "شكوى" in message or "complaint" in message:
            return "ESCALATION"

        data = chat_json([
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message}
        ])

        district = data.get("district")

        logger.info(f"LLM_LOCATION_RESULT district={district}")

        result = check_delivery_district(district)

        if not result["covered"]:

            logger.info("DELIVERY_NOT_COVERED")

            return "عذراً التوصيل غير متوفر لهذا الحي."

        state.district = result["district"]
        state.delivery_fee = result["delivery_fee"]
        state.location_confirmed = True

        logger.info(
            f"STATE district={state.district} delivery_fee={state.delivery_fee}"
        )

        logger.info("HANDOFF LocationAgent → OrderAgent")

        return f"تم تأكيد التوصيل إلى حي {state.district}."