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
    """天気名（例：「晴れ」）から、weathersテーブルのIDを取得する【デバッグ版】"""
    try:
        print(f"\n[デバッグ情報] get_weather_id_by_name が '{weather_name}' という引数で呼び出されました。")
        
        response = supabase.table('weather').select('id, weather_name').execute()
        
        if not response.data:
            print("  [デバッグ情報] データベースからデータを取得できませんでした。テーブルは空かもしれません。")
            return None

        print("  [デバッグ情報] データベース内のデータと比較を開始します...")
        for weather in response.data:
            # 比較している2つの値を詳しく表示する
            db_value = weather['weather_name']
            arg_value = weather_name
            print(f"  [比較中] DBの値: '{db_value}' ({len(db_value)}文字) <-> 引数の値: '{arg_value}' ({len(arg_value)}文字)")
            
            # 比較条件
            if db_value in arg_value:
                print(f"  [成功] 一致しました！ ID: {weather['id']} を返します。")
                return weather['id']

        print("  [デバッグ情報] ループが終了しましたが、一致するデータは見つかりませんでした。")
        return None
    except Exception as e:
        print(f"Error getting weather_id: {e}")
        return None

def get_feelings_id() -> int | None:
    """feelingsテーブルからランダムに気分のIDを1つ取得する"""
    try:
        response = supabase.table('feelings').select('id').execute()
        if not response.data:
            return None
        random_feelings = random.choice(response.data)
        return random_feelings['id']
    except Exception as e:
        print(f"Error getting random feelings_id: {e}")
        return None

def get_image_url(weather_id: int, feelings_id: int) -> str | None:
    """weather_idとmood_idにマッチする画像のURLを取得する"""
    try:
        # weather_idとmood_idの両方に一致する画像を検索
        response = supabase.table('images').select('image_url').eq('weather_id', weather_id).eq('feelings_id', feelings_id).execute()
        if not response.data:
            return None # 該当する画像がない
        
        # 該当する画像が複数あれば、その中からランダムに1つ選ぶ
        random_image = random.choice(response.data)
        return random_image['image_url']
    except Exception as e:
        print(f"Error getting image_url: {e}")
        return None
    