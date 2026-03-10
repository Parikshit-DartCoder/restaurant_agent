import tiktoken

enc = tiktoken.get_encoding("cl100k_base")

def estimate_tokens(text):

    return len(enc.encode(text))