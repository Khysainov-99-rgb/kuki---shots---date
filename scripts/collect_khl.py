import json
from datetime import datetime
import os

def collect_khl_matches():
    """Сбор матчей КХЛ"""
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Пока тестовые данные
        matches = [
            {
                "date": today,
                "league": "KHL",
                "home": "Ак Барс",
                "away": "Салават Юлаев",
                "home_shots": 35,
                "away_shots": 28,
                "result": "4:2"
            }
        ]
        
        # Сохраняем
        os.makedirs('data/khl', exist_ok=True)
        with open('data/khl/today.json', 'w') as f:
            json.dump(matches, f, indent=2, ensure_ascii=False)
        
        # Добавляем в историю
        history_file = 'recent_matches.json'
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                history = json.load(f)
        else:
            history = {"matches": []}
        
        for match in matches:
            history["matches"].append(match)
        
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Собрано {len(matches)} матчей КХЛ")
        
    except Exception as e:
        print(f"❌ Ошибка сбора КХЛ: {e}")

if __name__ == "__main__":
    collect_khl_matches()
