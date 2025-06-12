import os
from supabase import create_client, Client

# Supabaseクライアントを初期化
def init_supabase():
    """Supabaseクライアントを初期化する"""
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")
    supabase: Client = create_client(url, key)
    return supabase

# Supabaseクライアントのインスタンスを作成
supabase = init_supabase()

def get_weather_id_by_name(weather_name: str) -> int | None:
    """
    天気名を含むレコードのIDをデータベース関数を使って取得する
    """
    try:
        # DBに作成した 'find_weather_id_by_name' 関数を呼び出す
        response = supabase.rpc('find_weather_id_by_name', {'p_weather_name': weather_name}).execute()
        
        # response.data には関数の戻り値が直接入る
        if response.data:
            return response.data
        return None
    except Exception as e:
        print(f"Error getting weather_id: {e}")
        return None

def get_feelings_id() -> int | None:
    """
    ランダムな気分のIDをデータベース関数を使って取得する
    """
    try:
        # DBに作成した 'get_random_feeling_id' 関数を呼び出す
        response = supabase.rpc('get_random_feeling_id', {}).execute()

        if response.data:
            return response.data
        return None
    except Exception as e:
        print(f"Error getting random feelings_id: {e}")
        return None

def get_image_url(weather_id: int, feelings_id: int) -> str | None:
    """
    weather_idとfeelings_idにマッチする画像のURLをデータベース関数を使って取得する
    """
    try:
        # DBに作成した 'get_random_image_url' 関数を呼び出す
        params = {'p_weather_id': weather_id, 'p_feeling_id': feelings_id}
        response = supabase.rpc('get_random_image_url', params).execute()

        if response.data:
            return response.data
        return None
    except Exception as e:
        print(f"Error getting image_url: {e}")
        return None

# --- コードの実行例 ---
if __name__ == '__main__':
    # .envファイルから環境変数を読み込む場合 (python-dotenvが必要)
    # from dotenv import load_dotenv
    # load_dotenv()

    # 1. 天気名からIDを取得
    # 天気APIなどから取得した文字列を想定
    current_weather_text = "今日は一日中、晴れの予報です。" 
    weather_id = get_weather_id_by_name(current_weather_text)
    print(f"天気テキスト: '{current_weather_text}'")
    print(f"取得した天気ID: {weather_id}")

    if weather_id:
        # 2. ランダムな気分のIDを取得
        feelings_id = get_feelings_id()
        print(f"取得した気分ID: {feelings_id}")

        if feelings_id:
            # 3. 画像のURLを取得
            image_url = get_image_url(weather_id, feelings_id)
            print(f"取得した画像URL: {image_url}")