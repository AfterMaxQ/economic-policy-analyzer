import logging
import os
from datetime import datetime

def setup_logger(name, log_file=None, level=logging.INFO):
    """
    设置并返回一个日志记录器
    
    参数:
    name (str): 日志记录器名称
    log_file (str): 日志文件路径（可选）
    level: 日志级别，默认为INFO
    
    返回:
    logging.Logger: 配置好的日志记录器
    """
    
    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 创建格式器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 添加控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 如果指定了日志文件，则添加文件处理器
    if log_file:
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def setup_default_logger():
    """
    设置默认日志记录器，日志文件按日期命名
    
    返回:
    logging.Logger: 默认日志记录器
    """
    # 创建logs目录
    if not os.path.exists('logs'):
        os.makedirs('logs')
        
    # 按日期生成日志文件名
    today = datetime.now().strftime('%Y-%m-%d')
    log_file = f'logs/app_{today}.log'
    
    return setup_logger('economic_policy_analyzer', log_file)

# 使用示例
if __name__ == "__main__":
    # 设置默认日志记录器
    logger = setup_default_logger()
    
    # 测试日志记录
    logger.info("日志系统初始化完成")
    logger.warning("这是一个警告信息")
    logger.error("这是一个错误信息")