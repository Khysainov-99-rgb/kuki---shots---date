#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Сбор данных по матчам НХЛ
Версия: 1.0
"""

import json
import os
import sys
import logging
from datetime import datetime
from typing import List, Dict, Any

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/nhl_collector.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('nhl_collector')

class NHLDataCollector:
    """Сборщик данных по матчам НХЛ"""
    
    def __init__(self):
        self.data_dir = 'data/nhl'
        self.history_file = 'recent_matches.json'
        self.ensure_directories()
    
    def ensure_directories(self):
        """Создание необходимых директорий"""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        logger.info(f"Директории созданы: {self.data_dir}")
    
    def collect_today_matches(self) -> List[Dict[str, Any]]:
        """
        Сбор матчей на сегодня
        В реальном проекте здесь будет парсинг NHL API
        """
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Тестовые данные для проверки работы
        matches = [
            {
                "date": today,
                "league": "NHL",
                "home": "Нью-Йорк Рейнджерс",
                "away": "Бостон Брюинз",
                "home_shots": 32,
                "away_shots": 28,
                "result": "4:3 ОТ",
                "status": "completed",
                "source": "test_data"
            },
            {
                "date": today,
                "league": "NHL",
                "home": "Торонто Мэйпл Лифс",
                "away": "Монреаль Канадиенс",
                "home_shots": 35,
                "away_shots": 31,
                "result": "5:2",
                "status": "completed",
                "source": "test_data"
            },
            {
                "date": today,
                "league": "NHL",
                "home": "Эдмонтон Ойлерз",
                "away": "Калгари Флэймз",
                "home_shots": 0,
                "away_shots": 0,
                "result": "не начался",
                "status": "scheduled",
                "source": "test_data"
            }
        ]
        
        logger.info(f"Собрано {len(matches)} матчей НХЛ")
        return matches
    
    def save_today_matches(self, matches: List[Dict[str, Any]]):
        """Сохранение сегодняшних матчей в отдельный файл"""
        try:
            filename = f"{self.data_dir}/today.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(matches, f, ensure_ascii=False, indent=2)
            logger.info(f"Сохранено в {filename}")
        except Exception as e:
            logger.error(f"Ошибка сохранения today.json: {e}")
            raise
    
    def update_history(self, new_matches: List[Dict[str, Any]]):
        """Обновление общей истории матчей"""
        try:
            # Загружаем существующую историю
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            else:
                history = {"matches": []}
            
            # Добавляем новые матчи, которых ещё нет в истории
            for match in new_matches:
                # Проверяем, есть ли уже такой матч
                exists = any(
                    m.get('date') == match['date'] and 
                    m.get('home') == match['home'] and 
                    m.get('away') == match['away']
                    for m in history['matches']
                )
                
                if not exists and match.get('status') == 'completed':
                    history['matches'].append(match)
                    logger.info(f"Добавлен новый матч: {match['home']} vs {match['away']}")
            
            # Сохраняем обновлённую историю
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
            
            logger.info(f"История обновлена. Всего матчей: {len(history['matches'])}")
            
        except Exception as e:
            logger.error(f"Ошибка обновления истории: {e}")
            raise
    
    def run(self):
        """Основной метод запуска сбора данных"""
        try:
            logger.info("=" * 50)
            logger.info("ЗАПУСК СБОРА ДАННЫХ НХЛ")
            logger.info("=" * 50)
            
            # Собираем матчи
            matches = self.collect_today_matches()
            
            if not matches:
                logger.warning("Нет матчей для обработки")
                return 0
            
            # Сохраняем сегодняшние
            self.save_today_matches(matches)
            
            # Обновляем историю
            self.update_history(matches)
            
            logger.info("✅ Сбор данных НХЛ успешно завершён")
            return 0
            
        except Exception as e:
            logger.error(f"❌ Критическая ошибка: {e}")
            return 1

def main():
    """Точка входа"""
    collector = NHLDataCollector()
    sys.exit(collector.run())

if __name__ == "__main__":
    main()
