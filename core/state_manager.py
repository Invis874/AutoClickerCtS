"""
Менеджер состояния приложения
"""

import json
import os
from datetime import datetime
from typing import Dict, Any
from utils.logger import get_logger

class StateManager:
    def __init__(self, state_file: str = "resources/config/state.json"):
        self.logger = get_logger(__name__)
        self.state_file = state_file
        self.state = self._load_state()
        
    def _load_state(self) -> Dict[str, Any]:
        """Загрузить сохраненное состояние"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Ошибка загрузки состояния: {e}")
            
        return {
            'total_clicks': 0,
            'upgrades_purchased': 0,
            'session_start': None,
            'last_run': None
        }
        
    def save_state(self):
        """Сохранить текущее состояние"""
        try:
            os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
            self.state['last_run'] = datetime.now().isoformat()
            
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
                
            self.logger.debug("Состояние сохранено")
        except Exception as e:
            self.logger.error(f"Ошибка сохранения состояния: {e}")
            
    def increment_clicks(self, count: int = 1):
        """Увеличить счетчик кликов"""
        self.state['total_clicks'] += count
        
    def increment_upgrades(self, count: int = 1):
        """Увеличить счетчик улучшений"""
        self.state['upgrades_purchased'] += count
        
    def start_session(self):
        """Начать новую сессию"""
        self.state['session_start'] = datetime.now().isoformat()
        
    def end_session(self):
        """Завершить текущую сессию"""
        if self.state['session_start']:
            session_duration = datetime.now() - datetime.fromisoformat(
                self.state['session_start']
            )
            self.state['session_duration'] = str(session_duration)
            self.state['session_start'] = None
            
    def get_stats(self) -> Dict[str, Any]:
        """Получить статистику"""
        return self.state.copy()