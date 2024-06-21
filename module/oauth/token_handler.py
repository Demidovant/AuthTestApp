import json
import os
import jwt
from module.logger import logger

TOKEN_FILE = "logs/oauth/token.txt"
TOKEN_DECODED_FILE = "logs/oauth/token_decoded.txt"

for file in [TOKEN_FILE, TOKEN_DECODED_FILE]:
    path = os.path.dirname(file)
    if not os.path.exists(path):
        os.makedirs(path)
    with open(file, "w") as f:
        pass


def decode_token(token):
    decoded_data = jwt.decode(jwt=token,
                              algorithms=["HS256"],
                              verify=False,
                              options={"verify_signature": False})
    return decoded_data


def save_token(token):
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        f.write(token)
    logger.info(f"Token saved to {TOKEN_FILE}")


def save_decoded_token(decoded_data):
    with open(TOKEN_DECODED_FILE, "w", encoding="utf-8") as f:
        f.write(json.dumps(decoded_data, indent=4, ensure_ascii=False))
    logger.info(f"Decoded token saved to {TOKEN_DECODED_FILE}")


def read_decoded_token():
    with open(TOKEN_DECODED_FILE, "r", encoding="utf-8") as f:
        token_content = f.read()
    return token_content


def clear_tokens():
    with open(TOKEN_DECODED_FILE, "w", encoding="utf-8") as f:
        pass
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        pass


def get_username():
    username = ""
    attributes = ["sub", "uid", "mail", "email", "phone", "mobile"]
    for attr in attributes:
        if not username:
            try:
                with open(TOKEN_DECODED_FILE, "r", encoding="utf-8") as f:
                    username = json.load(f)[attr]
                    logger.info(f"Username: {username}")
            except:
                pass
    else:
        if not username:
            logger.warning("Can't get any USERNAME from token or no token")
            logger.warning(f"Tried to search {attributes} attributes")
        return username
