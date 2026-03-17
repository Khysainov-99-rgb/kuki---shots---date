#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Сбор данных по матчам КХЛ с официального сайта
Версия: 2.0 (реальный парсинг)
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
        logging.FileHandler('logs/khl_collector.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('khl_collector')

class KHLDataCollector:
    """Сборщик данных по матчам КХЛ с официального сайта"""
    
    def __init__(self):
        self.data_dir = 'data/khl'
        self.history_file = 'recent_matches.json'
        self.base_url = "https://text.khl.ru/api"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.ensure_directories()
    
    def ensure_directories(self):
        """Создание необходимых директорий"""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        logger.info(f"Директории созданы: {self.data_dir}")
    
    def get_match_ids_for_date(self, date: str) -> List[str]:
        """
        Получение списка ID матчей на указанную дату
        Использует официальный календарь КХЛ
        """
        try:
            # Формируем URL для календаря
            calendar_url = f"https://text.khl.ru/api/calendar/{date}"
            logger.info(f"Запрос календаря: {calendar_url}")
            
            response = requests.get(calendar_url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                match_ids = []
                
                # Парсим ответ календаря
                for match in data.get('matches', []):
                    match_id = match.get('id')
                    if match_id:
                        match_ids.append(str(match_id))
                        logger.info(f"Найден матч ID: {match_id} - {match.get('home', {}).get('name')} vs {match.get('away', {}).get('name')}")
                
                logger.info(f"Всего найдено матчей на {date}: {len(match_ids)}")
                return match_ids
            else:
                logger.warning(f"Не удалось получить календарь на {date}, статус: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Ошибка получения календаря: {e}")
            return []
    
    def get_match_stats(self, match_id: str) -> Optional[Dict[str, Any]]:
        """
        Получение статистики матча по ID из официального API
        """
        try:
            # Используем официальный API текстовой трансляции
            stats_url = f"https://text.khl.ru/api/match/{match_id}/stats"
            logger.info(f"Запрос статистики матча {match_id}")
            
            response = requests.get(stats_url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                logger.warning(f"Не удалось получить статистику матча {match_id}, статус: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка получения статистики матча {match_id}: {e}")
            return None
    
    def parse_match_data(self, match_id: str, stats_data: Dict) -> Optional[Dict[str, Any]]:
        """
        Парсинг данных матча в наш формат
        """
        try:
            # Получаем основную информацию о матче
            match_info = stats_data.get('match', {})
            
            # Названия команд
            home_team = match_info.get('home', {}).get('name', '')
            away_team = match_info.get('away', {}).get('name', '')
            
            if not home_team or not away_team:
                logger.warning(f"Не удалось определить названия команд для матча {match_id}")
                return None
            
            # Счёт
            home_score = match_info.get('home', {}).get('score', 0)
            away_score = match_info.get('away', {}).get('score', 0)
            
            # Статус матча
            status = match_info.get('status', '')
            is_completed = status == 'finished'
            
            # Броски в створ
            home_shots = 0
            away_shots = 0
            
            # Парсим статистику по периодам
            periods = stats_data.get('periods', [])
            for period in periods:
                home_shots += period.get('home', {}).get('shots_on_target', 0)
                away_shots += period.get('away', {}).get('shots_on_target', 0)
            
            # Если нет данных по периодам, пробуем взять общую статистику
            if home_shots == 0 and away_shots == 0:
                total_stats = stats_data.get('total', {})
                home_shots = total_stats.get('home', {}).get('shots_on_target', 0)
                away_shots = total_stats.get('away', {}).get('shots_on_target', 0)
            
            # Формируем результат
            result = f"{home_score}:{away_score}"
            if not is_completed:
                result = "матч не завершён"
            
            match_data = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "league": "KHL",
                "home": home_team,
                "away": away_team,
                "home_shots": home_shots,
                "away_shots": away_shots,
                "result": result,
                "status": "completed" if is_completed else "scheduled",
                "match_id": match_id,
                "source": "khl.ru"
            }
            
            logger.info(f"Обработан матч: {home_team} vs {away_team} - {result}, броски: {home_shots}:{away_shots}")
            return match_data
            
        except Exception as e:
            logger.error(f"Ошибка парсинга данных матча {match_id}: {e}")
            return None
    
    def collect_today_matches(self) -> List[Dict[str, Any]]:
        """
        Сбор матчей на сегодня через официальный API КХЛ
        """
        today = datetime.now().strftime("%Y-%m-%d")
        matches = []
        
        # Получаем ID матчей на сегодня
        match_ids = self.get_match_ids_for_date(today)
        
        if not match_ids:
            logger.info(f"На {today} матчей не найдено")
            return matches
        
        # Для каждого ID получаем статистику
        for match_id in match_ids:
            logger.info(f"Обработка матча ID: {match_id}")
            
            # Небольшая задержка, чтобы не нагружать API
            time.sleep(1)
            
            stats_data = self.get_match_stats(match_id)
            if stats_data:
                match_data = self.parse_match_data(match_id, stats_data)
                if match_data:
                    matches.append(match_data)
        
        logger.info(f"Собрано {len(matches)} матчей КХЛ")
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
                    m.get('match_id') == match.get('match_id') or
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
            logger.info("ЗАПУСК СБОРА ДАННЫХ КХЛ (РЕАЛЬНЫЙ ПАРСИНГ)")
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
            
            logger.info("✅ Сбор данных КХЛ успешно завершён")
            return 0
            
        except Exception as e:
            logger.error(f"❌ Критическая ошибка: {e}")
            return 1

def main():
    """Точка входа"""
    collector = KHLDataCollector()
    sys.exit(collector.run())

if __name__ == "__main__":
    main()
