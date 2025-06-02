from datetime import datetime
import pytz

#日本時間の取得
def get_current_japan_time():
    jst = pytz.timezone('Asia/Osaka')
    return datetime.now(jst)

#時間帯の分類
def get_time_zone():
    now = get_current_japan_time()
    hour = now.hour

    if 5 <= hour < 9:
        return "朝"
    elif 9 <= hour < 17:
        return "昼"
    elif 17 <= hour < 19:
        return "夕方"
    else:
        return "夜"

    
#時間帯に応じた返答
def get_greeting_by_time_zone(time_zone: str):
    greetings = {
        "朝": "おはよう！！",
        "昼": "こんにちは～",
        "夕方": "こんばんは",
        "夜": "遅くまでお疲れさま"
    }
    return greetings.get(time_zone, "こんにちは")