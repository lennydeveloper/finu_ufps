from jwt import encode

def generate_token(data: dict):
    token = encode(payload={**data})