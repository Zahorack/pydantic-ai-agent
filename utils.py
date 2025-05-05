import logging
import sys

from config import settings


def init_logging() -> None:
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s [%(levelname)s] [%(processName)s %(threadName)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("agent.log"),
        ],
    )
    logging.getLogger("urllib3").setLevel(settings.urllib_log_level)
    logging.getLogger("openai").setLevel(settings.openai_log_level)
    logging.getLogger("httpcore").setLevel("INFO")
