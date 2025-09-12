import os
import json
import logging
from logging.config import dictConfig
from datetime import datetime


class JsonFormatter(logging.Formatter):
    """JSON格式化器"""

    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "line": record.lineno,
            "message": record.getMessage(),
        }

        # 添加异常信息
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_record, ensure_ascii=False)


formatters = {
    "string": {
        "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        "datefmt": "%Y-%m-%d %H:%M:%S",
    },
    "json": {"()": JsonFormatter},
}

# 定义日志配置
log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": formatters,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": os.getenv("LOG_LEVEL", "INFO").upper(),
            "formatter": os.getenv("LOG_FORMAT", "string").lower(),
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "app": {
            "handlers": ["console"],
            "level": os.getenv("LOG_LEVEL", "INFO").upper(),
            "propagate": False,
        },
    },
    "root": {"handlers": ["console"], "level": os.getenv("LOG_LEVEL", "INFO").upper()},
}

# 应用配置
dictConfig(log_config)


logger = logging.getLogger("app")
