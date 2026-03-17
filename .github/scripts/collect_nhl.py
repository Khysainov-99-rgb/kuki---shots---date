#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Сбор данных по матчам НХЛ с официального NHL API
Версия: 1.0
"""

import json
import os
import sys
import logging
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import time

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
    """Сборщик данных по матчам НХЛ с официального NHL API"""
    
    def __init__(self):
        self.data_dir = 'data/nhl'
        self.history_file = 'recent_matches.json'
        self.base_url = "https://api-web.nhle.com/v1"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.ensure_directories()
    
    def ensure_directories(self):
        """Создание необходимых директорий"""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        logger.info(f"Директории созданы: {self.data_dir}")
    
    def get_schedule(self, date: str) -> Optional[Dict]:
        """
        Получение расписания матчей на указанную дату
        """
        try:
            # NHL API endpoint для расписания
            url = f"{self.base_url}/schedule/{date}"
            logger.info(f"Запрос расписания: {url}")
            
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Получено расписание на {date}")
                return data
            else:
                logger.warning(f"Не удалось получить расписание, статус: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка получения расписания: {e}")
            return None
    
    def get_game_stats(self, game_id: str) -> Optional[Dict]:
        """
        Получение статистики матча по ID
        """
        try:
            # NHL API для бокс-скора
            url = f"{self.base_url}/gamecenter/{game_id}/boxscore"
            logger.info(f"Запрос статистики матча {game_id}")
            
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                logger.warning(f"Не удалось получить статистику матча {game_id}, статус: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка получения статистики матча {game_id}: {e}")
            return None
    
    def parse_game_data(self, game_id: str, game_data: Dict, schedule_data: Dict) -> Optional[Dict[str, Any]]:
        """
        Парсинг данных матча в наш формат
        """
        try:
            # Получаем информацию о матче из расписания
            game_info = schedule_data.get('games', [{}])[0] if schedule_data.get('games') else {}
            
            # Названия команд
            home_team = game_info.get('homeTeam', {}).get('name', {}).get('default', '')
            away_team = game_info.get('awayTeam', {}).get('name', {}).get('default', '')
            
            if not home_team or not away_team:
                logger.warning(f"Не удалось определить названия команд для матча {game_id}")
                return None
            
            # Счёт
            home_score = game_data.get('homeTeam', {}).get('score', 0)
            away_score = game_data.get('awayTeam', {}).get('score', 0)
            
            # Броски в створ
            home_shots = game_data.get('homeTeam', {}).get('shots', 0)
            away_shots = game_data.get('awayTeam', {}).get('shots', 0)
            
            # Статус матча
            game_state = game_info.get('gameState', '')
            is_completed = game_state == 'OFF' or game_state == 'FINAL'
            
            # Формируем результат
            result = f"{home_score}:{away_score}"
            if not is_completed:
                result = "матч не завершён"
            
            match_data = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "league": "NHL",
                "home": home_team,
                "away": away_team,
                "home_shots": home_shots,
                "away_shots": away_shots,
                "result": result,
                "status": "completed" if is_completed else "scheduled",
                "game_id": game_id,
                "source": "nhl.com"
            }
            
            logger.info(f"Обработан матч: {home_team} vs {away_team} - {result}, броски: {home_shots}:{away_shots}")
            return match_data
            
        except Exception as e:
            logger.error(f"Ошибка парсинга данных матча {game_id}: {e}")
            return None
    
    def collect_today_matches(self) -> List[Dict[str, Any]]:
        """
        Сбор матчей на сегодня через официальный NHL API
        """
        today = datetime.now().strftime("%Y-%m-%d")
        matches = []
        
        # Получаем расписание на сегодня
        schedule = self.get_schedule(today)
        
        if not schedule or not schedule.get('gameWeek'):
            logger.info(f"На {today} матчей не найдено")
            return matches
        
        # Собираем все матчи из расписания
        all_games = []
        for game_week in schedule.get('gameWeek', []):
            all_games.extend(game_week.get('games', []))
        
        if not all_games:
            logger.info(f"На {today} матчей не найдено")
            return matches
        
        logger.info(f"Найдено матчей в расписании: {len(all_games)}")
        
        # Для каждого матча получаем детальную статистику
        for game in all_games:
            game_id = game.get('id')
            if not game_id:
                continue
            
            logger.info(f"Обработка матча ID: {game_id}")
            
            # Небольшая задержка, чтобы не нагружать API
            time.sleep(1)
            
            game_stats = self.get_game_stats(game_id)
            if game_stats:
                match_data = self.parse_game_data(str(game_id), game_stats, {'games': [game]})
                if match_data:
                    matches.append(match_data)
        
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
                    m.get('game_id') == match.get('game_id') or
                    (m.get('date') == match['date'] and 
                     m.get('home') == match['home'] and 
                     m.get('away') == match['away'])
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
