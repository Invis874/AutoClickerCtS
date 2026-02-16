# actions/popup_handler.py - с использованием OCR
import pyautogui
import time
from utils.logger import get_logger # Блокнот для записей
import pytesseract  # распознование текста OCR
# Укажи путь к установленному Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
from PIL import Image, ImageGrab

class PopupHandler:
    def __init__(self):
        self.logger = get_logger(__name__) # Даем детективу блокнот
        
        # Область где может появиться текст "Пропустить" / кординаты кнопки
        self.text_region = (690, 700, 1200, 840)
        
        # Координаты клика по кнопке (центр)
        self.click_coords = (961, 733)  # центр кнопки
        
    def check_popups(self):
        """Проверяем наличие текста 'Пропустить' в области"""
        try:
            # 1. Делаем скриншот области
            screenshot = ImageGrab.grab(bbox=self.text_region)
            
            # 2. Распознаем текст
            text = pytesseract.image_to_string(
                screenshot, 
                lang='rus',  # русский + английский
                config='--psm 6 --oem 3'  # предполагаем единый блок текста
            )
            
            # 3. Ищем ключевые слова
            text_lower = text.lower()
            
            if 'пропустить' in text_lower:
                self.logger.info("Найдено окно с кнопкой 'Пропустить'")
                return True, 'skip'
                
            if 'собрать' in text_lower:
                self.logger.info("Найдено окно с кнопкой 'Собрать'")
                return True, 'collect'
                
        except Exception as e:
            self.logger.error(f"Ошибка при распознавании текста: {e}")
        return False, None
        
    def handle_popup(self, popup_type):
        """Обрабатываем всплывающее окно"""
        if popup_type in ['skip', 'collect']:
            x, y = self.click_coords
            pyautogui.click(x, y)
            time.sleep(1)
            self.logger.info(f"Нажата кнопка '{popup_type}'")
            return True
        return False