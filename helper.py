import os
import logging
import sys

def get_current_directory() -> str:
    # 获取当前文件的绝对路径
    file_path = os.path.abspath(__file__)
    # 获取当前文件所在的目录
    file_directory = os.path.dirname(file_path)
    return file_directory

def logger(log_path: str=os.path.join(get_current_directory(),"logs","unknown.log")) -> logging.Logger:
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    LOG_LEVEL = logging.INFO

    logging.basicConfig(
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        stream=sys.stdout
    )

    logger = logging.getLogger("NewsGist")

    __all__ = ["logger"]

    # 创建日志文件
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    
    # 写入日志文件
    file_handler = logging.FileHandler(filename=log_path,encoding='utf-8')
    file_handler.setLevel(LOG_LEVEL)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(file_handler)
    return logger

