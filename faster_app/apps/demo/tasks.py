import asyncio
from datetime import datetime
from faster_app.settings.logging import logger


async def send_notification(email: str, message: str):
    """
    模拟发送通知的后台任务
    在实际应用中，这里可以是发送邮件、推送消息、处理数据等耗时操作
    """
    logger.info(f"[后台任务] 开始处理通知任务 - 收件人: {email}")

    # 模拟耗时操作（如调用邮件服务API）
    await asyncio.sleep(3)

    logger.info(f"[后台任务] 通知已发送给 {email}: {message}")
    logger.info(f"[后台任务] 任务完成时间: {datetime.now().isoformat()}")


def write_log_to_file(task_id: str, data: dict):
    """
    同步的后台任务示例 - 写入日志文件
    后台任务也可以是同步函数
    """
    logger.info(f"[后台任务] 记录任务 {task_id} 的数据: {data}")
    # 这里可以写入文件或执行其他同步操作
    logger.info("[后台任务] 日志记录完成")
