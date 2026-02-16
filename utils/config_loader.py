"""
Загрузка конфигурации из YAML/JSON файлов
"""

import yaml
import json
import os
from typing import Any, Dict
from utils.logger import get_logger

class Config:
    def __init__(self, config_path: str = "resources/config/settings.yaml"):
        self.logger = get_logger(__name__)
        self.config_path = config_path
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Загрузить конфигурацию из файла"""
        try:
            if not os.path.exists(self.config_path):
                self.logger.warning(f"Конфиг не найден: {self.config_path}")
                return self._get_default_config()
                
            with open(self.config_path, 'r', encoding='utf-8') as f:
                if self.config_path.endswith('.yaml') or self.config_path.endswith('.yml'):
                    config = yaml.safe_load(f)
                    # Убедимся что все нужные поля есть
                    return self._ensure_config_structure(config)
                elif self.config_path.endswith('.json'):
                    return json.load(f)
                else:
                    raise ValueError(f"Неподдерживаемый формат файла: {self.config_path}")
                    
        except Exception as e:
            self.logger.error(f"Ошибка загрузки конфигурации: {e}")
            return self._get_default_config()
            
    def _ensure_config_structure(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Убедиться что в конфиге есть все необходимые поля"""
        default_config = self._get_default_config()
        
        # Рекурсивно обновляем значения по умолчанию
        def update_dict(default, current):
            for key, value in default.items():
                if key not in current:
                    current[key] = value
                elif isinstance(value, dict) and isinstance(current.get(key), dict):
                    update_dict(value, current[key])
            return current
        
        return update_dict(default_config, config)
            
    def _get_default_config(self) -> Dict[str, Any]:
        """Конфигурация по умолчанию - ОБНОВЛЕННАЯ!"""
        return {
            'hotkeys': {
                'start_stop': 'F2',
                'pause': 'F3',
                'exit': 'F4',
                'calibrate': 'F1'
            },
            # Настройки кликера
            'click_interval': 0.1,
            'click_variance': 5,
            'consecutive_pause': 50,
            'consecutive_pause_duration': 0.1,
            
            # Проверки
            'upgrade_check_interval': 30,
            'popup_check_interval': 0.5,
            
            # Области экрана
            'main_click_area': {
                'x': 500,
                'y': 300
            },
            'upgrades_area': {
                'x1': 100,
                'y1': 150,
                'x2': 400,
                'y2': 600
            },
            
            # Настройки OCR
            'tesseract': {
                'path': None,
                'languages': 'rus+eng',
                'config': '--oem 3 --psm 6'
            },
            
            # Логирование
            'logging': {
                'file': 'logs/autoclicker.log',
                'level': 'INFO',
                'console': True
            }
        }
        
    def get(self, key: str, default: Any = None) -> Any:
        """
        Получить значение по ключу
        
        Args:
            key: Ключ в формате 'section.key' или просто 'key'
            default: Значение по умолчанию
            
        Returns:
            Значение конфигурации
        """
        try:
            # Поддержка вложенных ключей через точку
            keys = key.split('.')
            value = self.config
            
            for k in keys:
                if isinstance(value, dict):
                    value = value.get(k)
                else:
                    return default
                    
            return value if value is not None else default
        except (KeyError, TypeError, AttributeError):
            return default
            
    def set(self, key: str, value: Any):
        """Установить значение по ключу"""
        try:
            keys = key.split('.')
            config = self.config
            
            # Проходим по всем ключам кроме последнего
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            # Устанавливаем последний ключ
            config[keys[-1]] = value
            self.logger.info(f"Конфиг обновлен: {key} = {value}")
            
        except Exception as e:
            self.logger.error(f"Ошибка установки значения {key}: {e}")
            
    def save(self, custom_path: str = None):
        """Сохранить текущую конфигурацию"""
        try:
            path = custom_path or self.config_path
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                if path.endswith('.yaml') or path.endswith('.yml'):
                    yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
                elif path.endswith('.json'):
                    json.dump(self.config, f, indent=2, ensure_ascii=False)
                    
            self.logger.info(f"Конфигурация сохранена: {path}")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка сохранения конфигурации: {e}")
            return False