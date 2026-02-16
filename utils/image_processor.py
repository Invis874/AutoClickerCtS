"""
Обработка изображений и поиск шаблонов
"""

import cv2
import numpy as np
import pyautogui
from typing import Optional, Tuple
from utils.logger import get_logger

class ImageProcessor:
    def __init__(self):
        self.logger = get_logger(__name__)
        
    def capture_screen(self, region: Optional[tuple] = None) -> np.ndarray:
        """
        Захватить скриншот области экрана
        
        Args:
            region: (x, y, width, height) или None для полного экрана
            
        Returns:
            Изображение в формате OpenCV
        """
        try:
            if region:
                screenshot = pyautogui.screenshot(region=region)
            else:
                screenshot = pyautogui.screenshot()
                
            # Конвертируем PIL в OpenCV формат
            img_array = np.array(screenshot)
            return cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
        except Exception as e:
            self.logger.error(f"Ошибка захвата экрана: {e}")
            raise
            
    def find_template(
        self, 
        image: np.ndarray, 
        template_path: str,
        confidence: float = 0.8
    ) -> Optional[Tuple[int, int]]:
        """
        Найти шаблон на изображении
        
        Args:
            image: Изображение в котором ищем
            template_path: Путь к файлу шаблона
            confidence: Порог уверенности (0-1)
            
        Returns:
            Координаты центра шаблона или None
        """
        try:
            template = cv2.imread(template_path)
            if template is None:
                self.logger.error(f"Шаблон не найден: {template_path}")
                return None
                
            # Поиск шаблона
            result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val >= confidence:
                h, w = template.shape[:2]
                center_x = max_loc[0] + w // 2
                center_y = max_loc[1] + h // 2
                return center_x, center_y
                
            return None
            
        except Exception as e:
            self.logger.error(f"Ошибка поиска шаблона {template_path}: {e}")
            return None
            
    def save_template(self, image: np.ndarray, path: str):
        """Сохранить изображение как шаблон"""
        cv2.imwrite(path, image)
        self.logger.info(f"Шаблон сохранен: {path}")