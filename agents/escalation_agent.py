from utils.logger import get_logger

logger = get_logger()

class EscalationAgent:

    def run(self, message, state):

        logger.info("ESCALATION triggered")

        response = """
نعتذر عن المشكلة.

سيتم تحويلك الآن إلى أحد ممثلي خدمة العملاء لمساعدتك بشكل أفضل.
"""

        return response