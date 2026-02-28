import copy
import logging

class ColoredFormatter(logging.Formatter):
    LEVEL_COLORS = {
        logging.DEBUG:    "\033[36m",
        logging.INFO:     "\033[32m",
        logging.WARNING:  "\033[33m",
        logging.ERROR:    "\033[31m",
        logging.CRITICAL: "\033[35;1m",
    }
    LEVEL_ABBR = {
        "DEBUG":    "DEBG",
        "INFO":     "INFO",
        "WARNING":  "WARN",
        "ERROR":    "ERRO",
        "CRITICAL": "CRIT",
    }
    RESET = "\033[0m"
    BOLD  = "\033[1m"
    DIM   = "\033[2m"

    def format(self, record: logging.LogRecord) -> str:
        record = copy.copy(record)
        color = self.LEVEL_COLORS.get(record.levelno, self.RESET)
        abbr  = self.LEVEL_ABBR.get(record.levelname, record.levelname[:4].upper())
        record.levelname = f"{color}{self.BOLD}{abbr}{self.RESET}"
        return super().format(record)


def _setup() -> None:
    # basicConfig 只在 root logger 没有 handler 时生效，多次 import 也只初始化一次
    if logging.root.handlers:
        return
    handler = logging.StreamHandler()
    handler.setFormatter(ColoredFormatter(
        fmt=(
            "[%(levelname)s]"
            # " \033[2m%(asctime)s\033[0m"
            # " \033[34m%(name)s\033[0m"
            " \033[2m%(filename)s:%(lineno)d\033[0m"
            " %(message)s"
        ),
        # datefmt="%Y-%m-%d %H:%M:%S",
        datefmt="%H:%M:%S",
    ))
    logging.basicConfig(level=logging.DEBUG, handlers=[handler])


_setup()


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)