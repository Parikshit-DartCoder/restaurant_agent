import logging
import time


def get_logger(name="restaurant_agent"):

    logger = logging.getLogger(name)

    if not logger.handlers:

        logger.setLevel(logging.INFO)

        handler = logging.StreamHandler()

        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s | %(name)s | %(message)s"
        )

        handler.setFormatter(formatter)

        logger.addHandler(handler)

    return logger


# --------------------------------------------------
# AGENT OBSERVABILITY HELPERS
# --------------------------------------------------

def log_agent_trigger(logger, agent, message=None):

    if message:
        logger.info(f"AGENT_TRIGGER {agent} message='{message}'")
    else:
        logger.info(f"AGENT_TRIGGER {agent}")


def log_agent_handoff(logger, from_agent, to_agent):

    logger.info(f"HANDOFF {from_agent} → {to_agent}")


def log_state(logger, key, value):

    logger.info(f"STATE {key}={value}")


def log_llm_start(logger, agent):

    logger.info(f"LLM_START agent={agent}")
    return time.time()


def log_llm_end(logger, agent, start_time):

    latency = time.time() - start_time
    logger.info(f"LLM_END agent={agent} latency={latency:.3f}s")