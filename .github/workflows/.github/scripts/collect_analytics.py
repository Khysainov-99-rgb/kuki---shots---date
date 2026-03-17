import json
from datetime import datetime
import os

def collect_analytics():
    """Сбор аналитических данных"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    data = {
        "date": today,
        "source": "github-actions",
        "predictions": []
    }
    
    # Создаём папку, если её нет
    os.makedirs('data/analytics', exist_ok=True)
    
    # Сохраняем файл
    filename = f'data/analytics/{today}.json'
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Analytics saved to {filename}")

if __name__ == "__main__":
    collect_analytics()
