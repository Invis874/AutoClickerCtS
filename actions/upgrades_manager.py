"""
Менеджер улучшений - ПОЛНАЯ ВЕРСИЯ
"""

import time
import re
import pyautogui
from typing import List, Dict, Optional, Tuple
from utils.image_processor import ImageProcessor
from utils.text_recognizer import TextRecognizer
from utils.logger import get_logger

class Upgrade:
    def __init__(self, name: str, cost: int, position: Tuple[int, int], is_available: bool = False):
        self.name = name
        self.cost = cost
        self.position = position  # координаты кнопки покупки
        self.is_available = is_available  # зеленая ли кнопка
        self.priority = 0
        
    def __str__(self):
        status = "✅" if self.is_available else "❌"
        return f"{status} {self.name} (cost: {self.cost}, priority: {self.priority})"

class UpgradesManager:
    def __init__(self, config):
        self.logger = get_logger(__name__)
        self.image_processor = ImageProcessor()
        self.text_recognizer = TextRecognizer()
        
        # Координаты из конфига (нужно будет добавить)
        self.panel_open_button = config.get('upgrades.panel_open_button', (36, 428)) # Кординаты открытия понели
        self.generator_tab = config.get('upgrades.generator_tab', (140, 45))
        self.research_tab = config.get('upgrades.research_tab', (223, 45))
        self.buy_mode_button = config.get('upgrades.buy_mode_button', (465, 142))
        self.upgrades_list_region = config.get('upgrades.list_region', (10, 179, 546, 893))
        
        # Цвета для проверки
        self.buy_button_color = config.get('upgrades.buy_button_color', (34,76,62))  # зеленый
        self.color_threshold = config.get('upgrades.color_threshold', 50)
        
        # Состояние
        self.current_tab = None
        self.buy_mode = "1"  # "0", "1", "10", "100", "max"
        self.last_check_time = 0
        
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
                x, y = self.generator_tab
            elif tab_name == "research":
                x, y = self.research_tab
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
    
    def set_buy_mode_to_max(self) -> bool:
        """Установить режим покупки на 'купить круглый'"""
        try:
            max_attempts = 5
            x, y = self.buy_mode_button
            for attempt in range(max_attempts):
                # Проверяем текст на кнопке
                screenshot = self.image_processor.capture_screen(
                    region=(x-111, y-15, 222, 30)
                )
                text = self.text_recognizer.extract_text(screenshot)
                
                if "купить круглы" in text.lower():
                    self.buy_mode = "0"
                    self.logger.info("Режим покупки: КРУГЛЫЙ")
                    return True

                # Кликаем по кнопке выбора режима
                pyautogui.click(x, y)
                time.sleep(0.3)

                self.logger.info(f"Попытка {attempt+1}: текущий режим '{text}'")
            
            self.logger.warning("Не удалось установить режим 'купить круглый'")
            return False
            
        except Exception as e:
            self.logger.error(f"Ошибка установки режима покупки: {e}")
            return False
    
    def scan_available_upgrades(self) -> List[Upgrade]:
        """
        Сканирует доступные улучшения в текущем списке
        Разделяем блоки попиксельно, текст собираем из каждого блока отдельно
        """
        try:
            print("\n" + "="*70)
            print("🔍 СКАНИРОВАНИЕ УЛУЧШЕНИЙ (ПОБЛОЧНОЕ)")
            print("="*70)
            
            # Параметры блока
            BLOCK_HEIGHT = 99
            AVATAR_WIDTH = 91
            TEXT_X_OFFSET = 102
            TEXT_WIDTH = 266
            BUTTON_WIDTH = 182
            BUTTON_HEIGHT = 69
            
            upgrades = []
            
            # Определяем количество блоков в области
            region_height = self.upgrades_list_region[3]
            max_blocks = region_height // BLOCK_HEIGHT
            
            print(f"\n📏 Область сканирования: {self.upgrades_list_region}")
            print(f"   Высота области: {region_height}px")
            print(f"   Количество блоков: {max_blocks}")
            
            # Проходим по каждому блоку
            for block_num in range(max_blocks):
                # Y-координата начала блока
                block_y = self.upgrades_list_region[1] + (block_num * BLOCK_HEIGHT)
                
                print(f"\n🔸 БЛОК {block_num} (Y={block_y})")
                
                # 1. Текстовая область блока (название + описание)
                text_region = (
                    TEXT_X_OFFSET,                                   # x1
                    block_y,                                         # y1
                    TEXT_WIDTH,                                      # width
                    BLOCK_HEIGHT                                     # height
                )
                
                print(f"   📝 Текстовая область: {text_region}")
                
                # Скриншот и распознавание текста блока
                text_screenshot = self.image_processor.capture_screen(region=text_region)
                block_text = self.text_recognizer.extract_text(text_screenshot)
                block_lines = block_text.split('\n')
                
                # Очищаем строки
                block_lines = [line.strip() for line in block_lines if line.strip()]
                
                print(f"   Распознанный текст блока:")
                for idx, line in enumerate(block_lines):
                    print(f"     [{idx}] '{line}'")
                
                # 🔴 КЛЮЧЕВАЯ ПРОВЕРКА: Если в блоке нет текста или меньше 1 строки
                if len(block_lines) < 1:
                    print(f"   ⏹️ Блок {block_num} пустой. Сканирование остановлено.")
                    break
                
                # 2. Кнопка блока
                button_x = text_region[0] + TEXT_WIDTH + 2 # Кордината левого угла кнопки
                button_y = block_y + (BLOCK_HEIGHT - BUTTON_HEIGHT) // 2  # центр по вертикали
                
                button_region = (
                    button_x,
                    button_y,
                    BUTTON_WIDTH,
                    BUTTON_HEIGHT
                )
                
                print(f"   🖱️ Кнопка: центр ({button_x + BUTTON_WIDTH//2}, {button_y + BUTTON_HEIGHT//2})")
                print(f"   🖱️ Область кнопки: {button_region}")
                
                # Скриншот кнопки для получения цены
                button_screenshot = self.image_processor.capture_screen(region=button_region)
                button_text = self.text_recognizer.extract_text(button_screenshot)
                
                print(f"   💰 Текст кнопки: '{button_text}'")
                
                # Извлекаем цену из текста кнопки
                cost = self._extract_cost_from_button(button_text)
                
                if cost > 0:
                    print(f"   ✅ Цена распознана: {cost:.2e}")
                    
                    # Проверяем доступность по цвету
                    is_available = self._is_button_available(
                        button_x + BUTTON_WIDTH//2,
                        button_y + BUTTON_HEIGHT//2
                    )
                    print(button_x + BUTTON_WIDTH//2,
                        button_y + BUTTON_HEIGHT//2)
                    # Определяем тип улучшения по тексту блока
                    full_text = " ".join(block_lines).lower()
                    is_research = any([
                        'эффективнее' in full_text,
                        'открыть' in full_text,
                        'х' in full_text,
                        'x' in full_text
                    ])
                    
                    # Название улучшения (первая строка блока)
                    name = block_lines[0] if block_lines else f"Блок {block_num}"
                    
                    upgrade = Upgrade(
                        name=name[:50],
                        cost=cost,
                        position=(button_x + BUTTON_WIDTH//2, button_y + BUTTON_HEIGHT//2),
                        is_available=is_available
                    )
                    
                    upgrade.type = "research" if is_research else "generator"
                    upgrade.priority = self._calculate_priority(upgrade)
                    
                    print(f"   📊 Тип: {upgrade.type}, приоритет: {upgrade.priority:.0f}")
                    
                    upgrades.append(upgrade)
                else:
                    print(f"   ❌ Цена не распознана")
            
            print("\n" + "="*70)
            print(f"📊 ИТОГО: {len(upgrades)} улучшений")
            for u in upgrades:
                status = "✅" if u.is_available else "❌"
                print(f"  {status} [{u.type}] {u.name[:30]}... | цена: {u.cost:.2e} | приоритет: {u.priority:.0f}")
            print("="*70)
            
            # Сортируем: сначала доступные, потом по приоритету
            upgrades.sort(key=lambda x: (-x.is_available, -x.priority))
            
            self.logger.info(f"Найдено улучшений: {len(upgrades)}, доступно: {sum(1 for u in upgrades if u.is_available)}")
            return upgrades
            
        except Exception as e:
            self.logger.error(f"Ошибка сканирования улучшений: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _extract_cost_from_button(self, text: str) -> float:
        """Извлекает стоимость из текста кнопки"""
        try:
            print(f"      Парсинг цены из: '{text}'")
            
            # Ищем паттерн с Е (научная нотация)
            import re
            pattern = r'(\d+(?:[.,]\d+)?)\s*[ЕE]\s*(\d+)'
            match = re.search(pattern, text, re.IGNORECASE)
            
            if match:
                base = float(match.group(1).replace(',', '.'))
                exp = int(match.group(2))
                value = base * (10 ** exp)
                print(f"        Найдено: {base}Е{exp} = {value:.2e}")
                return value
            
            # Если не нашли научную нотацию, ищем просто число
            numbers = re.findall(r'[\d\s,]+', text)
            if numbers:
                clean = numbers[-1].replace(' ', '').replace(',', '.')
                if clean.replace('.', '').isdigit():
                    value = float(clean)
                    print(f"        Найдено простое число: {value}")
                    return value
            
        except Exception as e:
            print(f"      Ошибка парсинга: {e}")
        
        return 0.0
    
    def _is_button_available(self, x: int, y: int) -> bool:
        """Проверяет, доступна ли кнопка (зеленый цвет)"""
        try:
            # Получаем цвет пикселя в центре кнопки
            pixel_color = pyautogui.pixel(x, y)
            
            # Сравниваем с эталонным зеленым цветом
            color_diff = sum(abs(c1 - c2) for c1, c2 in zip(pixel_color, self.buy_button_color))
            
            return color_diff < self.color_threshold
        except Exception:
            return False
    
    def _extract_cost(self, text: str) -> int:
        """Извлечь стоимость из текста"""
        try:
            # Ищем числа (возможно с разделителями)
            numbers = re.findall(r'[\d\s,]+', text)
            for num_str in numbers:
                # Убираем пробелы и запятые
                clean_num = re.sub(r'[\s,]', '', num_str)
                if clean_num.isdigit():
                    return int(clean_num)
        except:
            pass
        return 0
    
    def _calculate_priority(self, upgrade: Upgrade) -> float:
        """Рассчитать приоритет улучшения"""
        priority = 0
        
        # Доступные улучшения имеют приоритет
        if upgrade.is_available:
            priority += 100
        
        # Веса ключевых слов
        keywords = {
            'клик': 50,
            'генератор': 40,
            'авто': 30,
            'золот': 20,
            'критич': 25,
            'множит': 35,
            'уровень': 15,
        }
        
        name_lower = upgrade.name.lower()
        for keyword, weight in keywords.items():
            if keyword in name_lower:
                priority += weight
        
        # Учитываем стоимость (чем дешевле, тем выше приоритет)
        if upgrade.cost > 0:
            priority += 1000.0 / upgrade.cost
        
        return priority
    
    def purchase_upgrade(self, upgrade: Upgrade) -> bool:
        """Купить улучшение"""
        try:
            if not upgrade.is_available:
                self.logger.info(f"Улучшение '{upgrade.name}' недоступно")
                return False
            
            x, y = upgrade.position
            pyautogui.click(x, y)
            time.sleep(0.5)
            
            self.logger.info(f"Куплено улучшение: {upgrade.name} (cost: {upgrade.cost})")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка покупки улучшения: {e}")
            return False
    
    def buy_all_available_generators(self) -> int:
        """
        Покупает все доступные улучшения генераторов
        Возвращает количество купленных
        """
        bought = 0
        
        # 1. Открываем панель
        if not self.open_panel():
            return 0
        
        # 2. Переключаемся на генераторы
        if not self.switch_to_tab("generator"):
            self.close_panel()
            return 0
        
        # 3. Устанавливаем режим "купить круглый"
        if not self.set_buy_mode_to_max():
            self.logger.warning("Продолжаем с текущим режимом покупки")
        
        # 4. Покупаем все доступные улучшения
        max_purchases = 20  # предохранитель от бесконечного цикла
        for _ in range(max_purchases):
            upgrades = self.scan_available_upgrades()
            
            # Ищем доступные улучшения генераторов
            available = [u for u in upgrades if u.is_available]
            
            if not available:
                break
            
            # Покупаем самое приоритетное
            best = available[0]
            if self.purchase_upgrade(best):
                bought += 1
                time.sleep(0.5)  # ждем обновления списка
            else:
                break
        
        # 5. Закрываем панель
        self.close_panel()
        
        self.logger.info(f"Куплено генераторов: {bought}")
        return bought
    
    def buy_best_research(self) -> bool:
        """
        Покупает лучшее доступное исследование
        """
        # 1. Открываем панель
        if not self.open_panel():
            return False
        
        # 2. Переключаемся на исследования
        if not self.switch_to_tab("research"):
            self.close_panel()
            return False
        
        # 3. Сканируем доступные улучшения
        upgrades = self.scan_available_upgrades()
        
        # 4. Ищем лучшее доступное
        available = [u for u in upgrades if u.is_available]
        
        if not available:
            self.logger.info("Нет доступных исследований")
            self.close_panel()
            return False
        
        # 5. Покупаем самое приоритетное
        best = available[0]
        success = self.purchase_upgrade(best)
        
        # 6. Закрываем панель
        self.close_panel()
        
        return success
    
    def manage_upgrades(self):
        """
        Основной метод управления улучшениями
        Вызывается периодически из основного цикла
        """
        try:
            # Сначала пробуем купить исследования (приоритет)
            if self.buy_best_research():
                self.logger.info("Куплено исследование")
                return
            
            # Если исследований нет, покупаем генераторы
            bought = self.buy_all_available_generators()
            if bought > 0:
                self.logger.info(f"Куплено генераторов: {bought}")
                
        except Exception as e:
            self.logger.error(f"Ошибка управления улучшениями: {e}")