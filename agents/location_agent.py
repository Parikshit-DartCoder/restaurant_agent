from services.llm_service import LLMUnavailableError, chat_json
from tools.delivery_tools import check_delivery_district
from utils.logger import get_logger

logger = get_logger()

SYSTEM_PROMPT = """
أنت مساعد لاستخراج اسم حي من رسالة مستخدم لمطعم في الرياض.
قد يكتب المستخدم بالعربية أو الإنجليزية أو لهجة أو Arabizi.

أعد JSON فقط بالشكل:
{"district": "<district or empty string>"}
"""


class LocationAgent:

    def run(self, district, state):
        result = check_delivery_district(district)

        logger.info(f"TOOL check_delivery_district({district})")
        logger.info(f"TOOL_RESULT {result}")

        if not result["covered"]:
            try:
                parsed = chat_json(
                    [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": district},
                    ]
                )
                llm_district = (parsed.get("district") or "").strip()
                if llm_district:
                    result = check_delivery_district(llm_district)
                    logger.info(f"LLM district candidate: {llm_district}")
                    logger.info(f"TOOL_RESULT after LLM district: {result}")
            except LLMUnavailableError as e:
                logger.warning(f"Location LLM unavailable: {e}")
            except Exception as e:
                logger.warning(f"Location LLM parse failed: {e}")

        if result["covered"]:
            state.district = result["district"]
            state.delivery_fee = result["delivery_fee"]
            return True

        return False