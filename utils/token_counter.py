try:
    import tiktoken
    _enc = tiktoken.get_encoding("cl100k_base")
except Exception:
    _enc = None


def estimate_tokens(text):
    text = str(text or "")
    if _enc is None:
        return max(1, len(text.split()))
    return len(_enc.encode(text))