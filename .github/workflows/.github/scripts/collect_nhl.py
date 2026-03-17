import json
from datetime import datetime
import os

def collect_nhl_matches():
    """Сбор матчей НХЛ"""
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Пока тестовые данные для НХЛ
        matches = [
            {
                "date": today,
                "league": "NHL",
                "home": "Нью-Джерси Дэвилз",
                "away": "Бостон Брюинз",
                "home_shots": 32,
                "away_shots": 28,
                "result": "4:3 ОТ"
            }
        ]
        
        # Создаём папку
        os.makedirs('data/nhl', exist_ok=True)
        
        # Сохраняем сегодняшние матчи
        with open('data/nhl/today.json', 'w') as f:
            json.dump(matches, f, indent=2, ensure_ascii=False)
        
        # Добавляем в общую историю
        history_file = 'recent_matches.json'
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                history = json.load(f)
        else:
            history = {"matches": []}
        
        for match in matches:
            # Проверяем, нет ли уже такого матча
            exists = any(
                m.get('date') == match['date'] and 
                m.get('home') == match['home'] and 
                m.get('away') == match['away'] 
                for m in history['matches']
            )
            if not exists:
                history['matches'].append(match)
        
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        
        print(f"✅ NHL: собран матч {matches[0]['home']} vs {matches[0]['away']}")
        
    except Exception as e:
        print(f"❌ Ошибка сбора НХЛ: {e}")

if __name__ == "__main__":
    collect_nhl_matches()
