import json
import logging
from logging.config import dictConfig
from datetime import datetime, timezone
from faster_app.settings.config import configs


class JsonFormatter(logging.Formatter):
    """JSON格式化器"""

    def format(self, record):
        log_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
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
    "STRING": {
        "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        "datefmt": "%Y-%m-%d %H:%M:%S",
    },
    "JSON": {"()": JsonFormatter},
}

# 定义日志配置
log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": formatters,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": configs.LOG_LEVEL.upper(),
            "formatter": configs.LOG_FORMAT.upper(),
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "app": {
            "handlers": ["console"],
            "level": configs.LOG_LEVEL.upper(),
            "propagate": False,
        },
    },
    "root": {"handlers": ["console"], "level": configs.LOG_LEVEL.upper()},
}

# 应用配置
dictConfig(log_config)


logger = logging.getLogger("app")
