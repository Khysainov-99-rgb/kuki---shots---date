import json
from datetime import datetime
import os
import sys

def collect_khl_matches():
    print("🚀 Запуск collect_khl.py")
    print(f"📂 Текущая папка: {os.getcwd()}")
    print(f"📄 Содержимое папки: {os.listdir('.')}")

    try:
        today = datetime.now().strftime("%Y-%m-%d")
        matches = [{
            "date": today,
            "league": "KHL",
            "home": "Ак Барс",
            "away": "Салават Юлаев",
            "home_shots": 35,
            "away_shots": 28,
            "result": "4:2"
        }]

        os.makedirs('data/khl', exist_ok=True)
        with open('data/khl/today.json', 'w') as f:
            json.dump(matches, f, indent=2, ensure_ascii=False)

        print(f"✅ KHL: {len(matches)} матчей записано")
        return 0

    except Exception as e:
        print(f"❌ Ошибка в collect_khl: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(collect_khl_matches())
