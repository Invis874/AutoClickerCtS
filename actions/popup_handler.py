# actions/popup_handler.py - с использованием OCR
import pyautogui
import time
from utils.logger import get_logger # Блокнот для записей
import pytesseract  # распознование текста OCR
# Укажи путь к установленному Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
from PIL import Image, ImageGrab
from typing import List, Tuple, Optional, Dict

class PopupHandler:
    def __init__(self):
        self.logger = get_logger(__name__) # Даем детективу блокнот
        
        # Словарь с предустановленными областями
        self.regions = {
            'skip_button': (690, 700, 1200, 840),      # кнопка пропуска
            'reward_window': (788, 248, 1138, 298),     # окно награды
        }
        
        # Предустановленные действия
        self.actions = {
            'skip': (961, 753),
            'collect': (961, 753),
            'center': (),
        }
        
        self.logger.info("Универсальный детектор инициализирован")

        # Область где может появиться текст "Пропустить" / кординаты кнопки
        self.text_region = (690, 700, 1200, 840)
        
        # Координаты клика по кнопке (центр)
        self.click_coords = (961, 753)  # центр кнопки

    def find_text_in_region(self, region: Tuple[int, int, int, int], 
                           target_texts: List[str], 
                           timeout: int = 5) -> Optional[str]:
        """
        Ищет указанные тексты в заданной области
        
        Args:
            region: (x1, y1, x2, y2) область поиска
            target_texts: список текстов для поиска
            timeout: максимальное время ожидания в секундах
            
        Returns:
            Найденный текст или None
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                screenshot = ImageGrab.grab(bbox=region)
                text = pytesseract.image_to_string(
                    screenshot, 
                    lang='rus',
                    config='--psm 6 --oem 3'
                ).lower()
                
                for target in target_texts:
                    if target.lower() in text:
                        self.logger.info(f"Найден текст: '{target}'")
                        return target
                
                time.sleep(0.3)
                
            except Exception as e:
                self.logger.error(f"Ошибка при поиске: {e}")
        
        self.logger.info(f"Текст {target_texts} не найден за {timeout} сек")
        return None
    
    def wait_and_click(self, region: Tuple[int, int, int, int], 
                      target_texts: List[str], 
                      click_coords: Tuple[int, int],
                      timeout: int = 10) -> bool:
        """
        Ждет появление текста и кликает по координатам
        
        Args:
            region: где ищем
            target_texts: что ищем
            click_coords: куда кликать
            timeout: сколько ждать
        """
        if self.find_text_in_region(region, target_texts, timeout):
            x, y = click_coords
            pyautogui.click(x, y)
            self.logger.info(f"Клик по {click_coords}")
            time.sleep(0.5)
            return True
        return False
    
    def click_until_text_appears(self, click_coords: Tuple[int, int],
                                click_interval: float,
                                region: Tuple[int, int, int, int],
                                target_texts: List[str],
                                max_clicks: int = 10) -> bool:
        """
        Кликает пока не появится нужный текст
        
        Args:
            click_coords: куда кликать
            click_interval: интервал между кликами
            region: где искать текст
            target_texts: что ищем
            max_clicks: максимум кликов
        """
        x, y = click_coords
        
        for i in range(max_clicks):
            # Проверяем не появился ли текст
            found = self.find_text_in_region(region, target_texts, timeout=1)
            if found:
                self.logger.info(f"Текст появился после {i} кликов")
                return True
            
            # Кликаем
            pyautogui.click(x, y)
            self.logger.debug(f"Клик #{i+1} по {click_coords}")
            time.sleep(click_interval)
        
        self.logger.warning(f"Текст не появился после {max_clicks} кликов")
        return False
        
    # Сохраняем старые методы для совместимости
    def check_popups(self):
        """Старый метод для обратной совместимости"""
        return self.find_text_in_region(
            self.regions['skip_button'],
            ['пропустить', 'собрать']
        ), None
    
    def handle_popup(self, popup_type):
        """Старый метод для обратной совместимости"""
        if popup_type in ['skip', 'collect']:
            return self.wait_and_click(
                self.regions['skip_button'],
                [popup_type],
                self.actions[popup_type],
                timeout=1
            )
        return False