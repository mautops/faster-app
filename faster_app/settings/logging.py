import json
import logging
import os
from datetime import UTC, datetime
from logging.config import dictConfig
from typing import Any

from faster_app.settings.config import configs
from faster_app.utils import BASE_DIR


class JsonFormatter(logging.Formatter):
    """JSON格式化器 - 增强版,包含更多上下文信息"""

    def format(self, record):
        log_record = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
            "pathname": record.pathname,
        }

        # 添加异常信息
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            log_record["exception_type"] = (
                record.exc_info[0].__name__ if record.exc_info[0] else None
            )

        # 添加进程和线程信息
        log_record["process_id"] = record.process
        log_record["thread_id"] = record.thread
        log_record["thread_name"] = record.threadName

        # 添加 extra 字段(结构化数据)
        # 这些字段会作为顶级字段,便于查询和分析
        for key, value in record.__dict__.items():
            if key not in {
                "name",
                "msg",
                "args",
                "created",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "thread",
                "threadName",
                "exc_info",
                "exc_text",
                "stack_info",
                "asctime",
                "taskName",
            }:
                log_record[key] = value

        return json.dumps(log_record, ensure_ascii=False)


formatters = {
    "STRING": {
        "format": "%(asctime)s [%(levelname)s] [%(name)s:%(lineno)d] %(funcName)s: %(message)s",
        "datefmt": "%Y-%m-%d %H:%M:%S",
    },
    "JSON": {"()": JsonFormatter},
}


def _get_log_file_path() -> str:
    """获取日志文件路径"""
    log_path = configs.LOG.FILE_PATH
    # 如果是相对路径,基于项目根目录
    if not os.path.isabs(log_path):
        log_path = os.path.join(BASE_DIR, log_path)
    return log_path


def _ensure_log_directory(log_file_path: str) -> None:
    """确保日志目录存在"""
    log_dir = os.path.dirname(log_file_path)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)


# 构建 handlers 配置
handlers_config: dict[str, dict[str, Any]] = {
    "console": {
        "class": "logging.StreamHandler",
        "level": configs.LOG.LEVEL.upper(),
        "formatter": configs.LOG.FORMAT.upper(),
        "stream": "ext://sys.stdout",
    },
}

# 如果启用文件日志,添加文件处理器(按天归档)
if configs.LOG.TO_FILE:
    log_file_path = _get_log_file_path()
    _ensure_log_directory(log_file_path)

    handlers_config["file"] = {
        "()": "logging.handlers.TimedRotatingFileHandler",
        "level": configs.LOG.LEVEL.upper(),
        "formatter": configs.LOG.FORMAT.upper(),
        "filename": log_file_path,
        "when": "midnight",  # 每天午夜滚动
        "interval": 1,  # 每 1 天
        "backupCount": configs.LOG.BACKUP_COUNT,  # 保留的备份文件数量
        "encoding": "utf-8",
        "utc": False,  # 使用本地时间
    }

# 确定使用的 handlers
handlers_list = ["console", "file"] if configs.LOG.TO_FILE else ["console"]

# 定义日志配置
log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": formatters,
    "handlers": handlers_config,
    "loggers": {
        "app": {
            "handlers": handlers_list,
            "level": configs.LOG.LEVEL.upper(),
            "propagate": False,
        },
        # 配置 uvicorn 的 logger,避免 uvicorn.error 名称引起误解
        "uvicorn": {
            "handlers": handlers_list,
            "level": configs.LOG.LEVEL.upper(),
            "propagate": False,
        },
        "uvicorn.error": {
            "handlers": handlers_list,
            "level": configs.LOG.LEVEL.upper(),
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": handlers_list,
            "level": configs.LOG.LEVEL.upper(),
            "propagate": False,
        },
    },
    "root": {"handlers": handlers_list, "level": configs.LOG.LEVEL.upper()},
}

# 应用配置
dictConfig(log_config)


logger = logging.getLogger("app")
