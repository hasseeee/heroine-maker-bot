import os
import psycopg

def connect_db():
    """データベースに接続し、接続オブジェクトを返す"""
    try:
        # 環境変数からデータベース接続URIを取得
        conn_str = os.environ.get("DATABASE_URL")
        # データベースに接続
        conn = psycopg.connect(conn_str)
        return conn
    except psycopg.OperationalError as e:
        print(f"データベース接続エラー: {e}")
        return None

def get_weather_id_by_name(weather_name: str) -> int | None:
    """天気名を含むレコードのIDをSQLで直接取得する"""
    conn = connect_db()
    if not conn:
        return None

    # SQLインジェクションを防ぐため、プレースホルダ(%s)を使用
    sql = "SELECT id FROM weather WHERE %s LIKE '%' || weather_name || '%'"

    try:
        # 'with'構文でカーソルを自動的に閉じる
        with conn.cursor() as cur:
            # SQLとパラメータを渡して実行
            cur.execute(sql, (weather_name,))
            # 結果を1件だけ取得
            result = cur.fetchone() 
            
            if result:
                return result[0] # 結果はタプル (値,) で返るので、最初の要素を取得
            return None
    except Exception as e:
        print(f"Error getting weather_id: {e}")
        return None
    finally:
        # 最後に必ず接続を閉じる
        conn.close()


def get_feelings_id() -> int | None:
    """ランダムな気分のIDをSQLで直接取得する"""
    conn = connect_db()
    if not conn:
        return None

    sql = "SELECT id FROM feelings ORDER BY RANDOM() LIMIT 1"

    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            result = cur.fetchone()
            if result:
                return result[0]
            return None
    except Exception as e:
        print(f"Error getting random feelings_id: {e}")
        return None
    finally:
        conn.close()

def get_image_url(weather_id: int, feelings_id: int) -> str | None:
    """weather_idとfeelings_idにマッチする画像のURLをSQLで直接取得する"""
    conn = connect_db()
    if not conn:
        return None
    
    # 2つのパラメータをプレースホルダで指定
    sql = """
        SELECT image_url 
        FROM images 
        WHERE weather_id = %s AND feelings_id = %s 
        ORDER BY RANDOM() 
        LIMIT 1
    """

    try:
        with conn.cursor() as cur:
            # パラメータはタプルで渡す
            cur.execute(sql, (weather_id, feelings_id))
            result = cur.fetchone()
            if result:
                return result[0]
            return None
    except Exception as e:
        print(f"Error getting image_url: {e}")
        return None
    finally:
        conn.close()

# --- コードの実行例 ---
if __name__ == '__main__':
    # .envファイルから環境変数を読み込む場合 (python-dotenvが必要)
    # from dotenv import load_dotenv
    # load_dotenv()
    
    current_weather_text = "今日は曇りのち晴れでしょう"
    weather_id = get_weather_id_by_name(current_weather_text)
    print(f"天気テキスト: '{current_weather_text}'")
    print(f"取得した天気ID: {weather_id}")

    if weather_id:
        feelings_id = get_feelings_id()
        print(f"取得した気分ID: {feelings_id}")
        if feelings_id:
            image_url = get_image_url(weather_id, feelings_id)
            print(f"取得した画像URL: {image_url}")