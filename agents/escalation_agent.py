from utils.logger import get_logger

logger = get_logger("restaurant_agent")


class EscalationAgent:

    def run(self, message, state):

        logger.info("AGENT_TRIGGER EscalationAgent")

        # reset conversation
        state.reset()

        return """
نعتذر عن المشكلة.

سيتم تحويلك إلى خدمة العملاء.

يمكنك بدء طلب جديد بكتابة:
مرحبا
"""