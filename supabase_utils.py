import os
import random
from supabase import create_client, Client

# Supabaseクライアントを初期化
def init_supabase():
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")
    supabase: Client = create_client(url, key)
    return supabase

supabase = init_supabase()

def get_weather_id_by_name(weather_name: str) -> int | None:
    """天気名（例：「晴れ」）から、weathersテーブルのIDを取得する"""
    try:
        # 天気名に部分一致するものを検索（例：「晴時々曇」でも「晴」でヒットさせるため）
        response = supabase.table('weathers').select('id, name').execute()
        for weather in response.data:
            if weather['name'] in weather_name:
                return weather['id']
        return None # 該当なし
    except Exception as e:
        print(f"Error getting weather_id: {e}")
        return None

def get_random_mood_id() -> int | None:
    """moodsテーブルからランダムに気分のIDを1つ取得する"""
    try:
        response = supabase.table('moods').select('id').execute()
        if not response.data:
            return None
        random_mood = random.choice(response.data)
        return random_mood['id']
    except Exception as e:
        print(f"Error getting random mood_id: {e}")
        return None

def get_image_url(weather_id: int, mood_id: int) -> str | None:
    """weather_idとmood_idにマッチする画像のURLを取得する"""
    try:
        # weather_idとmood_idの両方に一致する画像を検索
        response = supabase.table('images').select('image_url').eq('weather_id', weather_id).eq('mood_id', mood_id).execute()
        if not response.data:
            return None # 該当する画像がない
        
        # 該当する画像が複数あれば、その中からランダムに1つ選ぶ
        random_image = random.choice(response.data)
        return random_image['image_url']
    except Exception as e:
        print(f"Error getting image_url: {e}")
        return None