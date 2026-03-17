import json
from collections import defaultdict
import os

def update_calibration():
    """Автоматический пересчёт средних бросков на основе новых матчей"""
    
    # Загружаем текущую калибровку
    if not os.path.exists('calibration.json'):
        print("❌ calibration.json не найден")
        return
    
    with open('calibration.json', 'r') as f:
        calibration = json.load(f)
    
    # Загружаем новые матчи
    if not os.path.exists('recent_matches.json'):
        print("❌ recent_matches.json не найден")
        return
    
    with open('recent_matches.json', 'r') as f:
        matches_data = json.load(f)
    
    # Собираем статистику по командам
    team_stats = defaultdict(lambda: {'total_shots': 0, 'count': 0})
    
    for match in matches_data.get('matches', []):
        home = match.get('home')
        away = match.get('away')
        
        if match.get('home_shots', 0) > 0:
            team_stats[home]['total_shots'] += match['home_shots']
            team_stats[home]['count'] += 1
        
        if match.get('away_shots', 0) > 0:
            team_stats[away]['total_shots'] += match['away_shots']
            team_stats[away]['count'] += 1
    
    # Обновляем средние в калибровке
    updated = False
    for team, stats in team_stats.items():
        if stats['count'] > 0:
            avg = stats['total_shots'] / stats['count']
            if team in calibration['teams']:
                old_avg = calibration['teams'][team]['shots_avg']
                old_count = calibration['teams'][team]['matches']
                # Взвешенное среднее
                new_avg = (old_avg * old_count + avg * stats['count']) / (old_count + stats['count'])
                calibration['teams'][team]['shots_avg'] = round(new_avg, 1)
                calibration['teams'][team]['matches'] += stats['count']
                updated = True
                print(f"✅ {team}: {old_avg} → {round(new_avg, 1)}")
    
    if updated:
        calibration['last_updated'] = '2026-03-17'
        
        with open('calibration.json', 'w') as f:
            json.dump(calibration, f, indent=2, ensure_ascii=False)
        print("✅ Калибровка обновлена и сохранена")
    else:
        print("ℹ️ Нет новых данных для обновления")

if __name__ == "__main__":
    update_calibration()
