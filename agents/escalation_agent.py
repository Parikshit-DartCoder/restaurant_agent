from utils.logger import get_logger

logger = get_logger("restaurant_agent")


class EscalationAgent:

    def run(self, message, state):

        logger.info("AGENT_TRIGGER EscalationAgent")
        logger.info(f"ESCALATION_MESSAGE {message}")

        return """
نعتذر عن المشكلة.

سيتم تحويلك الآن إلى أحد ممثلي خدمة العملاء لمساعدتك بشكل أفضل.
"""