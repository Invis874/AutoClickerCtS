"""
Настройка логирования
"""

import logging
import os
from datetime import datetime
from typing import Optional

def setup_logger(
    name: str = "AutoClicker",
    log_file: Optional[str] = None,
    level: int = logging.INFO
) -> logging.Logger:
    """
    Настройка логгера
    
    Args:
        name: Имя логгера
        log_file: Путь к файлу логов
        level: Уровень логирования
        
    Returns:
        Настроенный логгер
    """
    # Создаем логгер
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Формат сообщений
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Консольный обработчик
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Файловый обработчик (если указан файл)
    if log_file:
        # Создаем директорию если нужно
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

# Глобальный логгер
_logger = None

def get_logger(name: str = None) -> logging.Logger:
    """
    Получить логгер по имени
    
    Args:
        name: Имя логгера (будет использовано имя модуля если не указано)
        
    Returns:
        Логгер
    """
    if name is None:
        # Получаем имя вызывающего модуля
        import inspect
        name = inspect.currentframe().f_back.f_globals.get('__name__', 'root')
    
    return logging.getLogger(name)