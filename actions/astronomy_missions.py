"""
Менеджер астрономических миссий
"""

import time
import pyautogui
from typing import List, Dict, Optional, Tuple
from utils.logger import get_logger
from utils.image_processor import ImageProcessor
from utils.text_recognizer import TextRecognizer

class AstronomyMissions:
    def __init__(self, config):
        self.logger = get_logger(__name__)
        self.config = config
        self.image_processor = ImageProcessor()
        self.text_recognizer = TextRecognizer()

        self.panel_open_button = config.get('upgrades.panel_open_button', (36, 428)) # Кординаты открытия понели
        
        # Загружаем настройки из конфига
        self.first_block_y = config.get('astronomy.first_block_y', 277)
        self.block_height = config.get('astronomy.block_height', 143)
        self.block_count = config.get('astronomy.block_count', 5)
        self.button_x = config.get('astronomy.button_x', 330)
        
        # Настройки выбора миссий
        self.mission_first_y = config.get('astronomy.mission_selection.first_y', 386)
        self.mission_item_height = config.get('astronomy.mission_selection.item_height', 127)
        self.mission_item_count = config.get('astronomy.mission_selection.item_count', 3)

        # Координаты кнопок типов миссий
        self.type_buttons = config.get('astronomy.mission_selection.type_buttons', {
            "Темная материя": [955, 350],
            "Карлик(звезда)": [780, 350],
            "Созвездие": [1060, 350],
            "Скидка": [1140, 350]
        })
        
        # Список доступных миссий
        self.available_missions = config.get('missions.available', [
            {"type": "Темная материя", "name": "Темная материя 1", "priority": 1},
            {"type": "Карлик(звезда)", "name": "Белый карлик I", "priority": 2},
            {"type": "Карлик(звезда)", "name": "Красный карлик II", "priority": 3},
            {"type": "Карлик(звезда)", "name": "Красный карлик III", "priority": 4},
            {"type": "Созвездие", "name": "Созвездие I", "priority": 5}
        ])
        
        self.logger.info("Менеджер астрономических миссий инициализирован")

    def open_panel(self) -> bool:
        """Открыть панель улучшений"""
        try:
            x, y = self.panel_open_button
            pyautogui.click(x, y)
            time.sleep(1)  # ждем анимацию выезда
            self.logger.info("Панель улучшений открыта")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка открытия панели: {e}")
            return False
    
    def close_panel(self) -> bool:
        """Закрыть панель улучшений"""
        try:
            # Клик вне панели или кнопка закрытия
            pyautogui.click(598, 428)  # клик в левый верхний угол
            time.sleep(0.5)
            self.logger.info("Панель улучшений закрыта")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка закрытия панели: {e}")
            return False

    def switch_to_tab(self, tab_name: str) -> bool:
        """Переключиться на вкладку (generator/research)"""
        try:
            if tab_name == "generator":
                return False
            elif tab_name == "research":
                return False
            elif tab_name == "mission":
                x, y = (310, 45)
            else:
                return False
            
            pyautogui.click(x, y)
            time.sleep(0.5)  # ждем загрузку списка
            self.current_tab = tab_name
            self.logger.info(f"Переключено на вкладку: {tab_name}")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка переключения вкладки: {e}")
            return False

    def _scroll_down(self, scroll_x, scroll_y, item_height):
        """
        Скроллит список миссий вниз
        """
        try:
            # Нажимаем и тянем вверх
            pyautogui.moveTo(scroll_x, scroll_y)
            pyautogui.drag(0, -item_height * 1.5, duration=0.5, button='left')
            
            print(f"         📜 Скролл вниз")
            time.sleep(0.5)
            
        except Exception as e:
            print(f"         ⚠️ Ошибка скролла: {e}")

    def run_missions(self):
        """
        Основной метод - запуск обработки всех миссий
        """
        print("\n" + "="*50)
        print("🔭 АСТРОНОМИЧЕСКИЕ МИССИИ")
        print("="*50)

        # 1. Открываем панель
        if not self.open_panel():
            return False
        
        if not self.switch_to_tab("mission"):
            self.close_panel()
            return False

        try: 
            self._scroll_down(self.button_x, 
                         self.first_block_y + (3 * (self.block_height + 14)) // 2, 
                         self.block_height)

            time.sleep(1)

            for i in range(5):  # сколько блоков видно одновременно
                current_y = self.first_block_y + (i * (self.block_height + 14))
                print(f"\n   БЛОК {i+1} (Y={current_y})")
                
                if self._is_mission_ready(current_y):
                    self._collect_mission(i, current_y)
                elif self._find_mission_available(current_y):
                    self._start_new_mission(i, current_y)
                else:
                    print(f"      ⏳ Не готова")
                    
                self.close_panel()
            
        except Exception as e:
            self.logger.error(f"Ошибка в астрономических миссиях: {e}")
            self.close_panel()
    
    def _is_mission_ready(self, block_y):
        """
        Проверяет, готова ли миссия (зеленая кнопка)
        """
        try:
            button_y = block_y + self.block_height // 2
            r, g, b = pyautogui.pixel(self.button_x, button_y)
            
            is_green = g > r + 30 and g > b + 30
            
            if is_green:
                print(f"      🟢 Готова к сбору! RGB({r},{g},{b})")
            else:
                print(f"      🔴 RGB({r},{g},{b})")
                
            return is_green
            
        except Exception as e:
            print(f"      ⚠️ Ошибка проверки цвета: {e}")
            return False
    
    def _collect_mission(self, block_num, block_y):
        """
        Собирает готовую миссию
        """
        try:
            button_y = block_y + self.block_height // 2
            pyautogui.click(self.button_x, button_y)
            print(f"      🖱️ Сбор миссии")
            time.sleep(1)
            
            # Запускаем новую миссию
            self._start_new_mission(block_num, block_y)
            
        except Exception as e:
            print(f"      ⚠️ Ошибка сбора: {e}")
    
    def _start_new_mission(self, block_num, block_y):
        """
        Запускает новую миссию в освободившемся блоке
        """
        try:
            # Ищем кнопку "МИССИЯ ДОСТУПНА"
            mission_pos = self._find_mission_available(block_y)
            
            if not mission_pos:
                print(f"      ⚠️ Кнопка 'МИССИЯ ДОСТУПНА' не найдена")
                return
            
            pyautogui.click(*mission_pos)
            print(f"      🖱️ Клик по 'МИССИЯ ДОСТУПНА'")
            time.sleep(1)
            
            # Выбираем миссию для этого блока
            self._select_mission_for_block(block_num)
            
        except Exception as e:
            print(f"      ⚠️ Ошибка запуска миссии: {e}")
    
    def _find_mission_available(self, block_y):
        """
        Ищет кнопку 'МИССИЯ ДОСТУПНА' в блоке
        """
        try:
            search_region = (self.button_x - 255, block_y + 40, 400, self.block_height - 70)
            screenshot = self.image_processor.capture_screen(region=search_region)
            text = self.text_recognizer.extract_text(screenshot)

            print(text)
            
            if "МИССИЯ ДОСТУПНА" in text:
                # Возвращаем центр блока
                return (self.button_x, block_y + self.block_height // 2)
                
        except Exception as e:
            print(f"      ⚠️ Ошибка поиска: {e}")
        
        return None
    
    def _select_mission_for_block(self, block_num):
        """
        Выбирает миссию для конкретного блока
        """
        if block_num >= len(self.available_missions):
            print(f"      ⚠️ Нет миссии для блока {block_num + 1}")
            return
        
        mission = self.available_missions[block_num]
        print(f"      📋 Установка: {mission['type']} - {mission['name']}")
        
        # Выбираем тип
        if mission['type'] in self.type_buttons:
            x, y = self.type_buttons[mission['type']]
            pyautogui.click(x, y)
            print(f"         🖱️ Тип: {mission['type']}")
            time.sleep(0.5)
        
        # Выбираем конкретную миссию
        mission_pos = self._find_mission_by_name(mission['name'])
        if mission_pos:
            pyautogui.click(*mission_pos)
            print(f"         🖱️ Миссия: {mission['name']}")
            time.sleep(0.5)
    
    def _find_mission_by_name(self, mission_name):
        """
        Ищет миссию только среди первых трёх (без скролла)
        """
        try:
            for i in range(self.mission_item_count):
                current_y = self.mission_first_y + (i * self.mission_item_height)
                
                text_region = (760, current_y, 285, self.mission_item_height - (self.mission_item_height // 2))
                screenshot = self.image_processor.capture_screen(region=text_region)
                text = self.text_recognizer.extract_text(screenshot).strip()
                
                print(f"         Строка {i+1}: '{text[:30]}...'")
                
                if mission_name in text:
                    center_x = 935
                    center_y = current_y + self.mission_item_height // 2
                    print(f"         ✅ Найдено!")
                    return (center_x, center_y)
            
            print(f"         ❌ Миссия не найдена в первых трёх")
            
        except Exception as e:
            print(f"      ⚠️ Ошибка поиска: {e}")
        
        return None