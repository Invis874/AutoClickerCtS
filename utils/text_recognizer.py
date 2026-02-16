"""
Распознавание текста с экрана
"""

import pytesseract
from PIL import Image
import cv2
import numpy as np
from typing import Optional
from utils.logger import get_logger

class TextRecognizer:
    def __init__(self, tesseract_path: Optional[str] = None):
        self.logger = get_logger(__name__)
        
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
            
        # Настройки для улучшения распознавания
        self.config = '--oem 3 --psm 6 -l rus+eng'
        
    def extract_text(self, image: np.ndarray) -> str:
        """
        Извлечь текст из изображения
        
        Args:
            image: Изображение в формате OpenCV
            
        Returns:
            Распознанный текст
        """
        try:
            # Подготовка изображения
            processed_image = self._preprocess_image(image)
            
            # Распознавание
            text = pytesseract.image_to_string(
                processed_image, 
                config=self.config
            )
            
            return text.strip()
            
        except Exception as e:
            self.logger.error(f"Ошибка распознавания текста: {e}")
            return ""
            
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Предобработка изображения для лучшего распознавания
        
        Args:
            image: Исходное изображение
            
        Returns:
            Обработанное изображение
        """
        # Конвертация в оттенки серого
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Увеличение контраста
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # Бинаризация
        _, binary = cv2.threshold(
            enhanced, 
            0, 255, 
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        
        # Уменьшение шума
        denoised = cv2.medianBlur(binary, 3)
        
        return denoised