import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime

os.makedirs("logs", exist_ok=True)

_loggers = {}

def setup_logger():
    log_format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    formatter = logging.Formatter(log_format, date_format)
    
    file_handler = RotatingFileHandler(
        "logs/os_manager.log",
        maxBytes=1024 * 1024,
        backupCount=3,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

def get_logger(module_name):
    if not logging.getLogger().handlers:
        setup_logger()
    
    if module_name not in _loggers:
        _loggers[module_name] = logging.getLogger(module_name)
    
    return _loggers[module_name]

def show_logs(n=50, level=None):
    log_file = "logs/os_manager.log"
    
    if not os.path.exists(log_file):
        print("Файл логов не найден")
        return
    
    level_map = {
        "DEBUG": 10,
        "INFO": 20,
        "WARNING": 30,
        "ERROR": 40,
        "CRITICAL": 50
    }
    
    min_level = level_map.get(level.upper(), 0) if level else 0
    
    with open(log_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    filtered_lines = []
    for line in lines:
        if min_level > 0:
            for lvl_name, lvl_num in level_map.items():
                if lvl_num >= min_level and f"| {lvl_name} |" in line:
                    filtered_lines.append(line)
                    break
        else:
            filtered_lines.append(line)
    
    last_lines = filtered_lines[-n:] if filtered_lines else []
    
    if not last_lines:
        print("Нет записей логов с указанным уровнем")
    else:
        print("\n" + "="*80)
        print(f"ПОСЛЕДНИЕ {len(last_lines)} ЗАПИСЕЙ ЛОГА")
        if level:
            print(f"Уровень: {level.upper()} и выше")
        print("="*80)
        for line in last_lines:
            print(line.rstrip())

if __name__ == "__main__":
    log = get_logger("test")
    log.debug("Отладочное сообщение")
    log.info("Информационное сообщение")
    log.warning("Предупреждение")
    log.error("Сообщение об ошибке")
    log.critical("Критическая ошибка")
    
    print("\n--- Показать все логи ---")
    show_logs()
    
    print("\n--- Показать только WARNING и выше ---")
    show_logs(level="WARNING")