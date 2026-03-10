from tools.delivery_tools import check_delivery_district
from utils.logger import get_logger

logger = get_logger()


class LocationAgent:

    def run(self, district, state):
        result = check_delivery_district(district)

        logger.info(f"TOOL check_delivery_district({district})")
        logger.info(f"TOOL_RESULT {result}")

        if result["covered"]:
            state.district = result["district"]
            state.delivery_fee = result["delivery_fee"]
            return True

        return False