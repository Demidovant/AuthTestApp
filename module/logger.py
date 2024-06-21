import logging
from logging.handlers import RotatingFileHandler
import os

LOG_FILE = "logs/log.txt"

for file in [LOG_FILE]:
    path = os.path.dirname(file)
    if not os.path.exists(path):
        os.makedirs(path)
    with open(file, "w") as f:
        pass

logger = logging.getLogger("AuthTestApp")
logger.setLevel(logging.DEBUG)
# formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler = RotatingFileHandler(LOG_FILE)
handler.setFormatter(formatter)
logger.addHandler(handler)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


def rotate_log(n):
    lines = []
    with open(LOG_FILE, "r") as f:
        for line in reversed(f.readlines()):
            lines.append(line)
            if len(lines) >= n:
                break
    with open(LOG_FILE, "w") as f:
        f.writelines(lines[::-1])


def read_log():
    with open(LOG_FILE, "r") as f:
        log_content = f.read()
    return log_content
