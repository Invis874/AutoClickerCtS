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
from utils.config_loader import Config
from utils.logger import get_logger

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
        
        # Компоненты системы
        self.clicker = Clicker(config=self.config)
        self.popup_handler = PopupHandler()
        self.upgrades_manager = UpgradesManager(config=self.config)
        
        # Состояние системы
        self.is_running = False
        self.is_paused = False
        self.current_mode = self.MODE_FREE
        self.thread: Optional[threading.Thread] = None
        
        # Настройки из конфига
        self.main_click_area = self.config.get('main_click_area')
        self.click_interval = self.config.get('click_interval', 0.1)
        self.popup_check_interval = self.config.get('popup_check_interval', 5)
        self.upgrade_check_interval = self.config.get('upgrade_check_interval', 30)
        
        # Настройка горячих клавиш
        self._setup_hotkeys()
        
        self.logger.info("Автокликер инициализирован")
        
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

        while self.is_running:
            try:
                if self.is_paused:
                    time.sleep(0.5)
                    continue
                
                current_time = time.time()

                # Выбираем поведение в зависимости от режима
                if self.current_mode == self.MODE_FREE:
                    self._free_click_loop()
                elif self.current_mode == self.MODE_SMART:
                    # Умный режим - передаем и получаем обновленные таймеры
                    last_popup_check, last_upgrade_check = self._smart_click_step(
                        current_time, last_popup_check, last_upgrade_check
                    )
                elif self.current_mode == self.MODE_LOCATION1:
                    self._location1_loop()
                elif self.current_mode == self.MODE_DINO:
                    self._dino_loop()
                elif self.current_mode == self.MODE_COSMOS:
                    self._cosmos_loop()
                    
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
        
    def _cosmos_loop(self):
        """
        Режим F3 - КОСМОС (заглушка)
        TODO: добавить логику позже
        """
        print("🔧 Режим 'Космос' пока не реализован")
        print("⏸️  Автоматическая пауза")
        
        if not self.is_paused:
            self.is_paused = True
            print("⏸️ Пауза")

    def _smart_click_step(self, current_time, last_popup, last_upgrade):
        """
        Режим F4 - УМНЫЙ КЛИК (с окнами и улучшениями)
        То что мы уже сделали
        """
        try:
            loop_start = time.time()
            # 1. Проверка всплывающих окон
            if current_time - last_popup > self.popup_check_interval:
                last_popup = current_time
                has_popup, popup_type = self.popup_handler.check_popups()
            
                if has_popup:
                    self.popup_handler.handle_popup(popup_type)
                    return last_popup, last_upgrade
                
            # 2. Периодическая проверка улучшений
            if current_time - last_upgrade > self.upgrade_check_interval:
                last_upgrade = current_time
                upgrade_start = time.time()
                self.upgrades_manager.manage_upgrades()  # ← ОДНА СТРОКА!
                upgrade_time = time.time() - upgrade_start
                print(f"⏱️  Проверка улучшений: {upgrade_time:.3f} сек")

                
            # 3. Основной клик
            self.clicker.click()

            # 4. Интервал между кликами
            interval_start = time.time()
            time.sleep(self.click_interval)
            interval_time = time.time() - interval_start
            
            # Общее время цикла
            loop_time = time.time() - loop_start
            
            # Выводим статистику каждые 100 циклов
            if int(time.time()) % 10 == 0:  # каждые 10 секунд
                print(f"📊 Цикл: {loop_time:.3f} сек | " 
                      f"Интервал: {interval_time:.3f} сек | "
                      f"Настройка: {self.click_interval} сек")

        except Exception as e:
            self.logger.error(f"Ошибка в основном цикле: {e}")
            time.sleep(1)

        return last_popup, last_upgrade

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