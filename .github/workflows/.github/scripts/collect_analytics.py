import json
from datetime import datetime
import os
import sys

def collect_analytics():
    print("🚀 Запуск collect_analytics.py")
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        data = {
            "date": today,
            "source": "github-actions",
            "predictions": []
        }
        os.makedirs('data/analytics', exist_ok=True)
        with open(f'data/analytics/{today}.json', 'w') as f:
            json.dump(data, f, indent=2)
        print("✅ Analytics collected")
        return 0
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(collect_analytics())
