import os
import logging
import logging.handlers
from configparser import ConfigParser


# 全局 logger 对象
logger = None


# 读取配置文件
def load_log_config(config_file='./config/config.ini'):
    # 检查文件是否存在
    if not os.path.exists(config_file):
        raise FileNotFoundError(f'配置文件 {config_file} 不存在')

    config = ConfigParser(interpolation=None)  # 禁用插值
    config.read(config_file, encoding='utf-8')

    # 检查是否有[log]部分
    if 'log' not in config:
        raise KeyError('配置文件中缺少 [log] 部分')

    return config['log']


# 初始化日志配置
def setup_logger():
    global logger  # 使用全局 logger 对象

    try:
        # 加载日志配置
        log_config = load_log_config()

        # 检查并创建日志目录
        log_dir = os.path.dirname(log_config['file_path'])
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # 检查并创建日志文件
        log_file = log_config['file_path']
        if not os.path.exists(log_file):
            open(log_file, 'w').close()

        # 配置日志
        logger = logging.getLogger('my_logger')  # 使用固定名称
        logger.setLevel(log_config['level'])

        # 日志格式
        formatter = logging.Formatter(
            fmt=log_config['format'],
            datefmt=log_config['date_format']
        )

        # 文件日志处理器（支持日志轮转）
        max_size = int(log_config['max_size'].split(';')[0].strip())  # 提取有效部分
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_file,
            maxBytes=max_size,
            backupCount=int(log_config['backup_count'])
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # 控制台日志处理器（可选）
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        print('日志配置已初始化')
    except Exception as e:
        print(f'日志配置失败: {e}')
        raise


# 其他模块调用日志配置
def get_logger():
    global logger
    if logger is None:
        # raise RuntimeError('日志配置未初始化，请先调用 setup_logger()')
        setup_logger()
    return logger


# 示例使用
if __name__ == '__main__':
    setup_logger()
    logger.info('日志配置已初始化，日志文件位于 log/log.txt')
    logger.debug('这是一个调试信息')  # 由于日志级别为INFO，此条不会记录
    logger.error('这是一个错误信息')
