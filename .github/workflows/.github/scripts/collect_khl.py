import json
from datetime import datetime
import os

def collect_khl_matches():
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
    
    print(f"✅ KHL: {len(matches)} матчей")

if __name__ == "__main__":
    collect_khl_matches()
