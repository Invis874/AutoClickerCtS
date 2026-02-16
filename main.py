#!/usr/bin/env python3
"""
Главный файл запуска AutoClickerCtS
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.autoclicker import AutoClicker
from utils.logger import setup_logger

def main():
    """Точка входа в программу"""
    print("=" * 50)
    print("AUTO CLICKER Click-to-Success")
    print("=" * 50)
    
    # Настройка логирования
    logger = setup_logger()
    logger.info("Запуск приложения")
    
    try:
        # Создание и запуск автокликера
        clicker = AutoClicker()
        clicker.run()
    except KeyboardInterrupt:
        print("\n\nПрограмма завершена пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        print(f"Ошибка: {e}")
        input("Нажмите Enter для выхода...")
        sys.exit(1)

if __name__ == "__main__":
    main()