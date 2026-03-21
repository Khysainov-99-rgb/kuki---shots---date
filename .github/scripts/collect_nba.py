#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Сбор данных по матчам НБА
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
        logging.FileHandler('logs/nba_collector.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('nba_collector')

class NBADataCollector:
    """Сборщик данных по матчам НБА с официального NBA API"""
    
    def __init__(self):
        self.data_dir = 'data/nba'
        self.history_file = 'recent_matches.json'
        self.base_url = "https://cdn.nba.com/static/json/liveData"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.ensure_directories()
    
    def ensure_directories(self):
        """Создание необходимых директорий"""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        logger.info(f"Директории созданы: {self.data_dir}")
    
    def get_today_scores(self) -> Optional[Dict]:
        """Получение результатов сегодняшних матчей"""
        try:
            today = datetime.now().strftime("%Y%m%d")
            url = f"https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                logger.info("Получены данные о сегодняшних матчах НБА")
                return data
            else:
                logger.warning(f"Не удалось получить данные, статус: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка получения данных: {e}")
            return None
    
    def parse_game_data(self, game: Dict) -> Dict[str, Any]:
        """Парсинг данных одного матча"""
        try:
            home_team = game['homeTeam']['teamName']
            away_team = game['awayTeam']['teamName']
            home_score = game['homeTeam']['score']
            away_score = game['awayTeam']['score']
            game_status = game['gameStatus']
            
            is_completed = game_status == 3
            
            match_data = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "league": "NBA",
                "home": home_team,
                "away": away_team,
                "home_score": home_score,
                "away_score": away_score,
                "result": f"{home_score}:{away_score}",
                "status": "completed" if is_completed else "scheduled",
                "game_id": game['gameId'],
                "source": "nba.com"
            }
            
            return match_data
            
        except Exception as e:
            logger.error(f"Ошибка парсинга данных матча: {e}")
            return None
    
    def collect_today_matches(self) -> List[Dict[str, Any]]:
        """Сбор матчей на сегодня"""
        matches = []
        
        scores_data = self.get_today_scores()
        
        if not scores_data:
            logger.info("Нет данных о матчах на сегодня")
            return matches
        
        games = scores_data.get('scoreboard', {}).get('games', [])
        
        for game in games:
            match_data = self.parse_game_data(game)
            if match_data:
                matches.append(match_data)
                logger.info(f"Обработан матч: {match_data['home']} vs {match_data['away']}")
        
        logger.info(f"Собрано {len(matches)} матчей НБА")
        return matches
    
    def update_history(self, new_matches: List[Dict[str, Any]]):
        """Обновление общей истории матчей"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            else:
                history = {"matches": []}
            
            for match in new_matches:
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
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            
            logger.info(f"История обновлена. Всего матчей: {len(history['matches'])}")
            
        except Exception as e:
            logger.error(f"Ошибка обновления истории: {e}")
            raise
    
    def run(self):
        """Основной метод запуска сбора данных"""
        try:
            logger.info("=" * 50)
            logger.info("ЗАПУСК СБОРА ДАННЫХ НБА")
            logger.info("=" * 50)
            
            matches = self.collect_today_matches()
            
            if not matches:
                logger.warning("Нет матчей для обработки")
                return 0
            
            self.update_history(matches)
            
            logger.info("✅ Сбор данных НБА успешно завершён")
            return 0
            
        except Exception as e:
            logger.error(f"❌ Критическая ошибка: {e}")
            return 1

def main():
    collector = NBADataCollector()
    sys.exit(collector.run())

if __name__ == "__main__":
    main()
