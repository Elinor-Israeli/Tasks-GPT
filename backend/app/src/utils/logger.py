import logging
from typing import Final

logger: Final[logging.Logger] = logging.getLogger("todoapp")
logger.setLevel(logging.DEBUG)

console_handler: logging.StreamHandler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

formatter: logging.Formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)


