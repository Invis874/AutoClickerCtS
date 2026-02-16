"""
Логика основного кликера
"""

import pyautogui
import random
import time
from typing import Tuple
from utils.logger import get_logger # Блокнот для записей

class Clicker:
    def __init__(self, config=None):
        self.logger = get_logger(__name__) # Дали блокнот для заметок
        self.config = config

        pyautogui.PAUSE = 0  # Убираем ВСЕ паузы между командами!
        # pyautogui.FAILSAFE = False  # Отключаем защиту (осторожно!)
        
        # Вычисляем координаты ОДИН РАЗ при создании
        if config:
            coords = config.get('main_click_area')
            if isinstance(coords, dict):
                self.x = coords.get('x', 500)
                self.y = coords.get('y', 300)
            else:
                self.x, self.y = 500, 300
        else:
            self.x, self.y = 500, 300
            
        print(f"⚡ Clicker создан с координатами: ({self.x}, {self.y})")
        
    def click(self):
        """Клик в заранее известные координаты"""
        pyautogui.click(self.x, self.y)
