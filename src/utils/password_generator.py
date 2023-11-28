import zlib
from base64 import urlsafe_b64encode as b64e, urlsafe_b64decode as b64d

def obscure(data: bytes) -> bytes:
    return b64e(zlib.compress(data, 9))

def unobscure(obscured: bytes) -> bytes:
    return zlib.decompress(b64d(obscured))

def get_encrypted_pass(password: str) -> str:
    return obscure(bytearray(password, 'utf-8')).decode()   

def decode_password(password: str) -> str:
    encoding_value: bytes = unobscure(bytearray(password, 'utf-8'))
    return encoding_value.decode()
    # byte_value: str = get_encrypted_pass(password)
    # encoding_value: bytes = unobscure(byte_value.encode())
    # return encoding_value.decode()
