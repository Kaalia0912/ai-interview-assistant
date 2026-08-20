"""简单日志：同时输出到控制台和 logs/app.log。"""
import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def _setup():
    logger = logging.getLogger("rag")
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    log_dir = BASE_DIR / "logs"
    log_dir.mkdir(exist_ok=True)
    fh = logging.FileHandler(log_dir / "app.log", encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    logger.propagate = False
    return logger


logger = _setup()
