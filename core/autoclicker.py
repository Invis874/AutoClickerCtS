"""
Основной класс автокликера - координирует все компоненты
"""

import time
import threading
import keyboard
import pyautogui
from typing import Optional, Dict
from actions.clicker import Clicker
from actions.popup_handler import PopupHandler
from actions.upgrades_manager import UpgradesManager
from actions.astronomy_missions import AstronomyMissions
from utils.config_loader import Config
from utils.logger import get_logger
from utils.image_processor import ImageProcessor
from utils.text_recognizer import TextRecognizer

class AutoClicker:
    # Режимы работы
    MODE_FREE = "free"        # F6 - свободный клик (кликает где мышь)
    MODE_LOCATION1 = "loc1"    # F1 - локация 1 (заглушка)
    MODE_DINO = "dino"         # F2 - динозавры (заглушка)  
    MODE_COSMOS = "cosmos"     # F3 - космос (заглушка)
    MODE_SMART = "smart"       # F4 - умный режим (с окнами/улучшениями)

    def __init__(self, config_path: str = "resources/config/settings.yaml"):
        self.logger = get_logger(__name__)
        self.config = Config(config_path)
        self.image_processor = ImageProcessor()
        self.text_recognizer = TextRecognizer()
        
        # Компоненты системы
        self.clicker = Clicker(config=self.config)
        self.popup_handler = PopupHandler()
        self.upgrades_manager = UpgradesManager(config=self.config)
        self.astronomy_missions = AstronomyMissions(self.config)
        
        # Состояние системы
        self.is_running = False
        self.is_paused = False
        self.current_mode = self.MODE_FREE
        self.thread: Optional[threading.Thread] = None
        
        # Настройки из конфига
        self.main_click_area = self.config.get('main_click_area')
        self.navigation_menu = self.config.get('navigation_menu')
        self.click_interval = self.config.get('click_interval', 0.1)
        self.popup_check_interval = self.config.get('popup_check_interval', 5)
        self.upgrade_check_interval = self.config.get('upgrade_check_interval', 30)
        
        # Настройка горячих клавиш
        self._setup_hotkeys()
        
        self.logger.info("Автокликер инициализирован")

    def _navigate_to_location(self, target_text, click_coords=(1868, 145), wait_for_popup=True):
        """
        Универсальная функция перехода в любую локацию
        
        Args:
            click_coords: (x, y) куда кликнуть для открытия
            target_text: текст который ищем (например "ЗА ПРЕДЕЛАМИ")
            wait_for_popup: ждать ли появление окна "Собрать"
        """
        print(f"\n🧭 НАВИГАЦИЯ: ищем '{target_text}'")
        
        try:
            # 1. Кликаем по входу
            pyautogui.click(*click_coords)
            print(f"   🖱️ Клик по {click_coords}")
            time.sleep(1)
            
            # 2. Ищем кнопку с нужным текстом
            button_pos = self._find_button_with_text(target_text)
            
            if not button_pos:
                print(f"   ❌ Кнопка '{target_text}' не найдена")
                return False
                
            print(f"   ✅ Найдена кнопка '{target_text}'")
            pyautogui.click(*button_pos)
            print(f"   🖱️ Клик по кнопке")
            
            # 3. Если нужно ждать окно "Собрать"
            if wait_for_popup:
                print("   ⏳ Ожидание загрузки...")
                
                # Ждем появления окна и закрываем его
                popup_closed = self._wait_for_popup_and_close(timeout=30)
                
                if popup_closed:
                    print("   ✅ Загрузка завершена, окно закрыто")
                    return True
                else:
                    print("   ⚠️ Таймаут ожидания окна")
            
            return True
                    
        except Exception as e:
            self.logger.error(f"Ошибка навигации: {e}")
            return False

    def _wait_for_popup_and_close(self, timeout=30):
        """
        Ждет появления окна "Собрать" и закрывает его
        Возвращает True если окно появилось и было закрыто
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Проверяем всплывающие окна
            if self.popup_handler.wait_and_click(self.popup_handler.regions['skip_button'], ['собрать'],
                                                                          self.popup_handler.actions['skip'], timeout=1):
                    return True
                
            time.sleep(0.5)
        
        print(f"   ⚠️ Окно не появилось за {timeout} секунд")
        return False

    def _find_button_with_text(self, target_text):
        """
        Ищет кнопку с заданным текстом в сплывающем окне
        Возвращает координаты центра или None
        """
         # Параметры из конфига
        first_y = 287          # Y координата первой кнопки
        button_height = 124    # высота одной кнопки
        button_count = 3       # количество кнопок
        button_x = 958         # X координата центра кнопки
        
        print(f"\n🔍 Ищем кнопку '{target_text}'...")
        
        # Проходим по всем кнопкам по порядку
        for i in range(button_count):
            # Y координата текущей кнопки
            current_y = first_y + (i * button_height + 12)
            
            # Область текста на кнопке
            text_region = (
                button_x - 250,       # координата начала области текста в кнопке
                current_y + 28,       # кордината Y
                503,                  # ширина области
                75                    # высота облости
            )
            
            # Скриншот и распознавание
            screenshot = self.image_processor.capture_screen(region=text_region)
            text = self.text_recognizer.extract_text(screenshot)
            
            print(f"   Кнопка {i+1}: '{text.strip()}'")
            
            # Если нашли нужный текст
            if target_text in text:
                # Центр кнопки
                button_y = current_y + button_height // 2
                print(f"   ✅ Нашли! Кнопка {i+1} в ({button_x}, {button_y})")
                return (button_x, button_y)
        
        print(f"   ❌ Кнопка '{target_text}' не найдена")
        return None
        
    def _setup_hotkeys(self):
        """Настройка горячих клавиш"""
        # Режимы
        keyboard.add_hotkey('F1', lambda: self.set_mode(self.MODE_LOCATION1))
        keyboard.add_hotkey('F2', lambda: self.set_mode(self.MODE_DINO))
        keyboard.add_hotkey('F3', lambda: self.set_mode(self.MODE_COSMOS))
        keyboard.add_hotkey('F4', lambda: self.set_mode(self.MODE_SMART))
        keyboard.add_hotkey('F6', lambda: self.set_mode(self.MODE_FREE))
        
        # Управление
        keyboard.add_hotkey('F5', self.toggle_pause)  # пауза всего
        keyboard.add_hotkey('F9', self.shutdown)      # выход из программы
        
        self.logger.info("Горячие клавиши настроены")

    def set_mode(self, mode: str):
        """Переключить режим работы"""
        if self.is_running:
            self.stop()  # останавливаем текущий режим
        
        self.current_mode = mode
        mode_names = {
            self.MODE_LOCATION1: "ЛОКАЦИЯ 1 (F1)",
            self.MODE_DINO: "ДИНОЗАВРЫ (F2)",
            self.MODE_COSMOS: "КОСМОС (F3)",
            self.MODE_SMART: "УМНЫЙ РЕЖИМ (F4)",
            self.MODE_FREE: "СВОБОДНЫЙ КЛИК (F6)"            
        }
        
        print(f"\n🔄 Выбран режим: {mode_names.get(mode, mode)}")
        print("   Нажмите F5 для запуска")
                
    def _main_loop(self):
        """Основной рабочий цикл - выбор режима"""
        last_popup_check = time.time()
        last_upgrade_check = time.time()
        last_missions_check = time.time()

        while self.is_running:
            try:
                if self.is_paused:
                    time.sleep(0.5)
                    continue
                
                current_time = time.time()

                # Выбираем поведение в зависимости от режима
                if self.current_mode == self.MODE_FREE:
                    self._free_click_loop()
                elif self.current_mode == self.MODE_LOCATION1:
                    self._location1_loop()
                elif self.current_mode == self.MODE_DINO:
                    self._dino_loop()
                elif self.current_mode == self.MODE_COSMOS:
                    last_popup_check, last_missions_check = self._cosmos_loop(
                        current_time, last_popup_check, last_missions_check
                    )
                elif self.current_mode == self.MODE_SMART:
                    # Умный режим - передаем и получаем обновленные таймеры
                    last_popup_check, last_upgrade_check, last_missions_check = self._smart_click_step(
                        current_time, last_popup_check, last_upgrade_check, last_missions_check
                    )
                    
            except Exception as e:
                self.logger.error(f"Ошибка в основном цикле: {e}")
                time.sleep(1)

    def _location1_loop(self):
        """
        Режим F1 - ЛОКАЦИЯ 1 (заглушка)
        TODO: добавить логику позже
        """
        print("🔧 Режим 'Локация 1' пока не реализован")
        print("⏸️  Автоматическая пауза")
        
        # Явно ставим паузу, если не на паузе
        if not self.is_paused:
            self.is_paused = True
            print("⏸️ Пауза")
        
    def _dino_loop(self):
        """
        Режим F2 - ДИНОЗАВРЫ (заглушка)
        TODO: добавить логику позже
        """
        print("🔧 Режим 'Динозавры' пока не реализован")
        print("⏸️  Автоматическая пауза")
        
        if not self.is_paused:
            self.is_paused = True
            print("⏸️ Пауза")
        
    def _cosmos_loop(self, current_time, last_popup, last_cosmos):
        """
        Режим F3 - КОСМОС (только клики и миссии, без улучшений)
        """
        try:
            # 1. Проверка всплывающих окон
            if current_time - last_popup > self.popup_check_interval:
                last_popup = current_time
                if self.popup_handler.wait_and_click(self.popup_handler.regions['skip_button'], ['пропустить','собрать'],
                                                                          self.popup_handler.actions['skip'], timeout=1):
                    return last_popup, last_cosmos

            # 2. КАЖДЫЕ 15 МИНУТ - ПЕРЕХОД В КОСМОС
            if current_time - last_cosmos > 1 * 60:
                # Запускаем астрономические миссии
                self.astronomy_missions.run_missions()
                
                # Обновляем время последнего перехода
                last_cosmos = current_time
                    
            # 3. Основной клик
            self.clicker.click()

        except Exception as e:
            self.logger.error(f"Ошибка в основном цикле: {e}")
            time.sleep(1)

        return last_popup, last_cosmos

    def _smart_click_step(self, current_time, last_popup, last_upgrade, last_cosmos):
        """
        Режим F4 - УМНЫЙ КЛИК (с окнами и улучшениями)
        То что мы уже сделали
        """
        try:
            loop_start = time.time()
            # 1. Проверка всплывающих окон
            if current_time - last_popup > self.popup_check_interval:
                last_popup = current_time
                if self.popup_handler.wait_and_click(self.popup_handler.regions['skip_button'], ['пропустить','собрать'],
                                                                          self.popup_handler.actions['skip'], timeout=1):
                    return last_popup, last_upgrade, last_cosmos

            # 2. КАЖДЫЕ 15 МИНУТ - ПЕРЕХОД В КОСМОС
            if current_time - last_cosmos > 1 * 60:
                print("\n⏰ 15 МИНУТ - ПЕРЕХОД В КОСМОС")
                
                # Переходим в "ЗА ПРЕДЕЛАМИ"
                success = self._navigate_to_location(
                    click_coords=(1868, 145),  # координаты меню перехода
                    target_text="ЗА ПРЕДЕЛАМИ"
                )
                
                if success:
                    # Запускаем астрономические миссии
                    self.astronomy_missions.run_missions()

                    # Переходим в "ИССЛЕДОВАНИЕ"
                    success = self._navigate_to_location(
                        click_coords=(1868, 145),  # координаты меню перехода
                        target_text="ИССЛЕДОВАНИЕ"
                    )
                
                # Обновляем время последнего перехода
                last_cosmos = current_time
                
            # 3. Периодическая проверка улучшений
            if current_time - last_upgrade > self.upgrade_check_interval:
                last_upgrade = current_time
                upgrade_start = time.time()
                self.upgrades_manager.manage_upgrades()  # ← ОДНА СТРОКА!
                upgrade_time = time.time() - upgrade_start
                print(f"⏱️  Проверка улучшений: {upgrade_time:.3f} сек")

                
            # 4. Основной клик
            self.clicker.click()
            
            # Общее время цикла
            loop_time = time.time() - loop_start
            
            # Выводим статистику каждые 100 циклов
            if int(time.time()) % 10 == 0:  # каждые 10 секунд
                print(f"📊 Цикл: {loop_time:.3f} сек")

        except Exception as e:
            self.logger.error(f"Ошибка в основном цикле: {e}")
            time.sleep(1)

        return last_popup, last_upgrade, last_cosmos

    def _free_click_loop(self):
        """
        Режим F6 - СВОБОДНЫЙ КЛИК
        Кликает там, где находится мышь
        """
        try:
            # Кликаем в текущей позиции курсора
            pyautogui.click()
            time.sleep(self.click_interval)
            
        except Exception as e:
            self.logger.error(f"Ошибка в свободном режиме: {e}")
            time.sleep(1)
                
    def start(self):
        """Запустить автокликер"""
        if not self.is_running:
            self.is_running = True
            self.is_paused = False
            
            self.thread = threading.Thread(target=self._main_loop, daemon=True)
            self.thread.start()
            
            mode_names = {
                self.MODE_FREE: "СВОБОДНЫЙ",
                self.MODE_LOCATION1: "ЛОКАЦИЯ 1",
                self.MODE_DINO: "ДИНОЗАВРЫ",
                self.MODE_COSMOS: "КОСМОС",
                self.MODE_SMART: "УМНЫЙ"
            }
            
            self.logger.info(f"Автокликер запущен в режиме: {mode_names.get(self.current_mode, self.current_mode)}")
            print(f"\n✅ Запущен режим: {mode_names.get(self.current_mode, self.current_mode)}")
            print("   F5 - пауза, F9 - выход")
            
    def stop(self):
        """Остановить автокликер"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=2)
        self.logger.info("Автокликер остановлен")
        print("⏹️ Автокликер остановлен")
        
    def toggle_pause(self):
        """Поставить/снять паузу (F5)"""
        if not self.is_running:
            # Если не запущен - запускаем
            self.start()
        else:
            # Если запущен - переключаем паузу
            self.is_paused = not self.is_paused
            state = "ПАУЗА" if self.is_paused else "ПРОДОЛЖЕНИЕ"
            self.logger.info(f"Автокликер: {state}")
            print(f"⏸️ {state}")
        
    def shutdown(self):
        """Полный выход из программы (F9)"""
        print("\n👋 Выход из программы...")
        self.stop()
        time.sleep(0.5)
        exit(0)
            
    def run(self):
        """Основной метод запуска приложения"""
        print("=" * 60)
        print("🎮 МУЛЬТИРЕЖИМНЫЙ АВТОКЛИКЕР")
        print("=" * 60)
        
        print("\n📌 РЕЖИМЫ РАБОТЫ:")
        print("  F1 - Локация 1     (заглушка)")
        print("  F2 - Динозавры     (заглушка)")
        print("  F3 - Космос        (заглушка)")
        print("  F4 - Умный режим   (окна + улучшения)")
        print("  F6 - Свободный клик (клик где мышь)")
        
        print("\n🎮 УПРАВЛЕНИЕ:")
        print("  F5 - Пауза/Продолжить")
        print("  F9 - Выход")
        
        print(f"\n⚡ Программа ожидает команды...")
        print("=" * 60)
        
        # Блокируем основной поток до выхода
        keyboard.wait('F9')
        self.shutdown()