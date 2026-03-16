import requests
import json
from datetime import datetime
import os
from bs4 import BeautifulSoup

def collect_all_prematch_data():
    """Сбор всех предматчевых данных"""
    
    today = datetime.now().strftime("%Y-%m-%d")
    current_hour = datetime.now().hour
    
    print(f"📊 Сбор предматчевых данных на {today}")
    
    predictions = {
        "date": today,
        "khl": [],
        "nhl": [],
        "odds": [],
        "expert_picks": []
    }
    
    # Сбор с live-result.com
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        url = "https://www.live-result.com/hockey/russia-khl/"
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            predictions["khl"].append({
                "source": "live-result",
                "timestamp": datetime.now().isoformat(),
                "status": "collected"
            })
    except Exception as e:
        print(f"Ошибка сбора: {e}")
    
    # Сбор коэффициентов
    try:
        odds_url = "https://www.livecup.run/hockey/matches/today/"
        response = requests.get(odds_url, headers=headers, timeout=10)
        if response.status_code == 200:
            predictions["odds"].append({
                "source": "livecup",
                "timestamp": datetime.now().isoformat()
            })
    except Exception as e:
        print(f"Ошибка сбора коэффициентов: {e}")
    
    # Сохраняем
    filename = f"data/analytics/prematch_{today}.json"
    os.makedirs('data/analytics', exist_ok=True)
    
    with open(filename, 'w') as f:
        json.dump(predictions, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Данные сохранены: {filename}")
    return predictions

def main():
    print("🚀 Запуск сбора данных")
    collect_all_prematch_data()
    print("✅ Сбор завершён")

if __name__ == "__main__":
    main()
