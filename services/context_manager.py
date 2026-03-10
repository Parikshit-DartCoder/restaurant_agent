from utils.token_counter import estimate_tokens

MAX_HISTORY = 6

def build_context(history):

    truncated = history[-MAX_HISTORY:]

    tokens = estimate_tokens(str(truncated))

    return truncated, tokens