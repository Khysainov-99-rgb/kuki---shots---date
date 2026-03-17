import json
from datetime import datetime
import os

def collect_analytics():
    today = datetime.now().strftime("%Y-%m-%d")
    data = {"date": today, "source": "test", "predictions": []}
    
    os.makedirs('data/analytics', exist_ok=True)
    with open(f'data/analytics/{today}.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print("✅ Analytics collected")

if __name__ == "__main__":
    collect_analytics()
