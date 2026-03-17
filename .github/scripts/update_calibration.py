#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Обновление калибровки KUKI-SHOTS на основе новых матчей
Версия: 1.0
"""

import json
import os
import sys
import logging
from datetime import datetime
from collections import defaultdict
from typing import Dict, Any, List

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/calibration.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('calibration')

class CalibrationUpdater:
    """Обновление калибровки KUKI-SHOTS"""
    
    def __init__(self):
        self.calibration_file = 'calibration.json'
        self.history_file = 'recent_matches.json'
        self.backup_dir = 'backups/calibration'
        self.ensure_directories()
    
    def ensure_directories(self):
        """Создание необходимых директорий"""
        os.makedirs(self.backup_dir, exist_ok=True)
        os.makedirs('logs', exist_ok=True)
    
    def load_json(self, filename: str) -> Dict:
        """Безопасная загрузка JSON файла"""
        try:
            if not os.path.exists(filename):
                logger.warning(f"Файл {filename} не найден")
                return {} if 'calibration' not in filename else {"teams": {}}
            
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга {filename}: {e}")
            return {} if 'calibration' not in filename else {"teams": {}}
        except Exception as e:
            logger.error(f"Ошибка загрузки {filename}: {e}")
            return {} if 'calibration' not in filename else {"teams": {}}
    
    def save_json(self, filename: str, data: Dict):
        """Безопасное сохранение JSON файла"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Сохранено в {filename}")
        except Exception as e:
            logger.error(f"Ошибка сохранения {filename}: {e}")
            raise
    
    def create_backup(self):
        """Создание резервной копии калибровки"""
        try:
            if os.path.exists(self.calibration_file):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = f"{self.backup_dir}/calibration_{timestamp}.json"
                
                with open(self.calibration_file, 'r', encoding='utf-8') as src:
                    with open(backup_file, 'w', encoding='utf-8') as dst:
                        dst.write(src.read())
                
                logger.info(f"Резервная копия создана: {backup_file}")
        except Exception as e:
            logger.error(f"Ошибка создания резервной копии: {e}")
    
    def calculate_team_averages(self, matches: List[Dict]) -> Dict[str, Dict]:
        """Расчёт средних бросков по командам"""
        team_stats = defaultdict(lambda: {'total_shots': 0, 'games': 0})
        
        for match in matches:
            # Проверяем наличие данных о бросках
            if match.get('home_shots', 0) > 0:
                team = match.get('home')
                shots = match.get('home_shots', 0)
                if team and shots > 0:
                    team_stats[team]['total_shots'] += shots
                    team_stats[team]['games'] += 1
            
            if match.get('away_shots', 0) > 0:
                team = match.get('away')
                shots = match.get('away_shots', 0)
                if team and shots > 0:
                    team_stats[team]['total_shots'] += shots
                    team_stats[team]['games'] += 1
        
        # Вычисляем средние
        averages = {}
        for team, stats in team_stats.items():
            if stats['games'] > 0:
                avg = stats['total_shots'] / stats['games']
                averages[team] = {
                    'shots_avg': round(avg, 1),
                    'games': stats['games'],
                    'total_shots': stats['total_shots']
                }
                logger.info(f"Команда {team}: {avg:.1f} бросков ({stats['games']} игр)")
        
        return averages
    
    def update_calibration(self, new_averages: Dict[str, Dict]):
        """Обновление файла калибровки"""
        try:
            # Загружаем текущую калибровку
            calibration = self.load_json(self.calibration_file)
            
            if 'teams' not in calibration:
                calibration['teams'] = {}
            
            # Обновляем данные
            updates_count = 0
            for team, new_data in new_averages.items():
                if team in calibration['teams']:
                    old_data = calibration['teams'][team]
                    # Взвешенное среднее с учётом предыдущих игр
                    total_games = old_data.get('matches', 0) + new_data['games']
                    weighted_avg = (
                        (old_data.get('shots_avg', 0) * old_data.get('matches', 0) +
                         new_data['shots_avg'] * new_data['games']) / total_games
                    )
                    calibration['teams'][team] = {
                        'shots_avg': round(weighted_avg, 1),
                        'matches': total_games
                    }
                else:
                    calibration['teams'][team] = {
                        'shots_avg': new_data['shots_avg'],
                        'matches': new_data['games']
                    }
                updates_count += 1
                logger.info(f"Обновлена калибровка для {team}")
            
            # Обновляем метаданные
            calibration['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            calibration['total_teams'] = len(calibration['teams'])
            
            # Сохраняем обновлённую калибровку
            self.save_json(self.calibration_file, calibration)
            
            logger.info(f"✅ Калибровка обновлена для {updates_count} команд")
            
        except Exception as e:
            logger.error(f"Ошибка обновления калибровки: {e}")
            raise
    
    def run(self):
        """Основной метод запуска обновления калибровки"""
        try:
            logger.info("=" * 50)
            logger.info("ЗАПУСК ОБНОВЛЕНИЯ КАЛИБРОВКИ")
            logger.info("=" * 50)
            
            # Создаём резервную копию
            self.create_backup()
            
            # Загружаем историю матчей
            history = self.load_json(self.history_file)
            matches = history.get('matches', [])
            
            if not matches:
                logger.warning("Нет матчей для анализа")
                return 0
            
            logger.info(f"Загружено {len(matches)} матчей из истории")
            
            # Рассчитываем средние
            averages = self.calculate_team_averages(matches)
            
            if not averages:
                logger.warning("Нет данных для обновления калибровки")
                return 0
            
            # Обновляем калибровку
            self.update_calibration(averages)
            
            logger.info("✅ Обновление калибровки успешно завершено")
            return 0
            
        except Exception as e:
            logger.error(f"❌ Критическая ошибка: {e}")
            return 1

def main():
    """Точка входа"""
    updater = CalibrationUpdater()
    sys.exit(updater.run())

if __name__ == "__main__":
    main()
