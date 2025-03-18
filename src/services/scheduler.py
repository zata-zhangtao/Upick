from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from src.db import refresh_content
from src.log import get_logger

logger = get_logger("services.scheduler")

# 设置日志记录


# 全局调度器实例
scheduler = None

def job_listener(event):
    """任务执行监听器，记录任务执行情况"""
    if event.exception:
        logger.error(f"任务执行失败: {event.job_id}, 异常: {event.exception}")
    else:
        logger.info(f"任务执行成功: {event.job_id}, 返回值: {event.retval}")

def initialize_scheduler():
    """初始化并配置调度器"""
    global scheduler
    
    # 创建后台调度器（不阻塞主线程）
    scheduler = BackgroundScheduler(
        job_defaults={
            'coalesce': True,       # 错过的任务只执行一次
            'max_instances': 1,     # 同一任务最大并发实例数
            'misfire_grace_time': 60 * 5  # 任务错过执行时间的宽限期（秒）
        }
    )
    
    # 添加任务监听器
    scheduler.add_listener(job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
    
    return scheduler

def add_refresh_job(hours=1, minutes=0):
    """添加内容刷新任务到调度器
    
    Args:
        hours (int): 任务间隔小时数，默认1小时
        minutes (int): 任务间隔分钟数，可与hours组合使用
    
    Returns:
        str: 任务ID
    """
    global scheduler
    
    # 确保调度器已初始化
    if scheduler is None:
        initialize_scheduler()
    
    # 设置间隔触发器
    trigger = IntervalTrigger(
        hours=hours,
        minutes=minutes
    )
    
    # 添加任务
    job = scheduler.add_job(
        func=refresh_content,            # 要执行的函数
        trigger=trigger,                  # 触发器
        id='refresh_content_job',         # 任务唯一ID
        name='刷新订阅内容',               # 任务名称
        replace_existing=True,           # 如果任务ID已存在则替换
        max_instances=1                  # 最大并发实例数
    )
    
    logger.info(f"已添加定时刷新任务，间隔：{hours}小时{minutes}分钟，任务ID: {job.id}")
    return job.id

def add_daily_refresh_job(hour=0, minute=0):
    """添加每日定时刷新任务
    
    Args:
        hour (int): 每天执行的小时（0-23）
        minute (int): 执行的分钟（0-59）
    
    Returns:
        str: 任务ID
    """
    global scheduler
    
    # 确保调度器已初始化
    if scheduler is None:
        initialize_scheduler()
    
    # 设置Cron触发器
    trigger = CronTrigger(
        hour=hour,
        minute=minute
    )
    
    # 添加任务
    job = scheduler.add_job(
        func=refresh_content,
        trigger=trigger,
        id='daily_refresh_job',
        name='每日定时刷新',
        replace_existing=True
    )
    
    logger.info(f"已添加每日定时刷新任务，时间：{hour}:{minute}，任务ID: {job.id}")
    return job.id

def remove_job(job_id):
    """移除指定的任务
    
    Args:
        job_id (str): 要移除的任务ID
    """
    global scheduler
    if scheduler and scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
        logger.info(f"已移除任务: {job_id}")

def start_scheduler():
    """启动调度器"""
    global scheduler
    if scheduler is None:
        initialize_scheduler()
    
    if not scheduler.running:
        scheduler.start()
        logger.info("调度器已启动")

def shutdown_scheduler():
    """关闭调度器"""
    global scheduler
    if scheduler and scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("调度器已关闭")
        scheduler = None