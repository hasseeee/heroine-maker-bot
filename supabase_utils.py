import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

def connect_db():
    """データベースに接続し、接続オブジェクトを返す"""

    
    # 環境変数からデータベース接続URIを取得
    conn_str = os.environ.get("DATABASE_URL")

    # ▼▼▼▼▼ ここからデバッグコードを追加 ▼▼▼▼▼
    print("="*20)
    print("--- データベース接続情報のデバッグ開始 ---")

    if conn_str:
        print(f"プログラムが読み込んだDATABASE_URL: {conn_str}")
        
        # 接続文字列を分解して、より詳しく見てみる
        try:
            user_pass_part = conn_str.split('@')[0].split('//')[1]
            host_part = conn_str.split('@')[1]
            password = user_pass_part.split(':')[1]
            
            print(f"  [確認] ホスト名とポート: {host_part}")
            print(f"  [確認] ユーザー名: {user_pass_part.split(':')[0]}")
            print(f"  [確認] パスワードの文字数: {len(password)}文字")

        except IndexError:
            print("  [エラー] DATABASE_URLの形式が正しくないようです。")

    else:
        print("プログラムはDATABASE_URLを読み込めていません。Noneです。")

    print("--- デバッグ終了 ---")
    print("="*20)
    # ▲▲▲▲▲ ここまでデバッグコードを追加 ▲▲▲▲▲

    try:
        # 環境変数からデータベース接続URIを取得
        conn_str = os.environ.get("DATABASE_URL")
        # データベースに接続
        conn = psycopg.connect(conn_str)
        return conn
    except psycopg.OperationalError as e:
        print(f"データベース接続エラー: {e}")
        return None

def insert_weather(weather_name: str) -> int | None:
    """
    新しい天気をweatherテーブルに追加し、その新しいIDを返す
    """
    print(f"データベースに新しい天気 '{weather_name}' を追加します。")
    conn = connect_db()
    if not conn:
        return None

    # RETURNING id を使うことで、INSERTと同時に新しく作られたIDを取得できる
    sql = "INSERT INTO weather (weather_name) VALUES (%s) RETURNING id"
    
    try:
        with conn.cursor() as cur:
            # executeの戻り値として新しいIDを受け取る
            cur.execute(sql, (weather_name,))
            new_id = cur.fetchone()[0]
            conn.commit()  # 変更を確定
            print(f"✅ 新しい天気ID: {new_id} として登録しました。")
            return new_id
    except Exception as e:
        conn.rollback()  # エラー時は変更を取り消す
        print(f"天気追加エラー: {e}")
        return None
    finally:
        if conn:
            conn.close()


def get_weather_id_by_name(weather_name: str) -> int | None:
    """天気名を含むレコードのIDをSQLで直接取得する"""
    conn = connect_db()
    if not conn:
        return None

    # SQLインジェクションを防ぐため、プレースホルダ(%s)を使用
    sql = "SELECT id FROM weather WHERE weather_name ILIKE %s"

    try:
        # 'with'構文でカーソルを自動的に閉じる
        with conn.cursor() as cur:
            # SQLとパラメータを渡して実行
            cur.execute(sql, (weather_name,))
            # 結果を1件だけ取得
            result = cur.fetchone() 
            
            # もしIDが見つかれば、そのIDを返す
            if result:
                print(f"既存の天気 '{weather_name}' (ID: {result[0]}) を見つけました。")
                return result[0] # 結果はタプル (値,) で返るので、最初の要素を取得

            # 見つからなかった場合
            else:
                print(f"既存の天気に '{weather_name}' が見つかりませんでした。")
                # この後の finally で接続が閉じてしまうので、ここで一度接続を閉じる
                conn.close()
                # 新しく天気を追加して、そのIDを返す
                return insert_weather(weather_name)
                
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


def get_id_by_exact_name(table_name: str, column_name: str, name: str) -> int | None:
    """テーブル名、カラム名、名称を指定して、完全一致するIDを取得する汎用関数"""
    conn = connect_db()
    if not conn:
        return None
    
    # SQLインジェクションを防ぐため、テーブル名とカラム名は安全な文字列か検証（簡易的）
    if not table_name.isalnum() or not column_name.isalnum():
        print("エラー: テーブル名またはカラム名に不正な文字が含まれています。")
        return None

    # 動的にSQLを組み立てるが、値はプレースホルダで安全に渡す
    sql = f"SELECT id FROM {table_name} WHERE {column_name} = %s"
    
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (name,))
            result = cur.fetchone()
            return result[0] if result else None
    except Exception as e:
        print(f"Error getting id from {table_name}: {e}")
        return None
    finally:
        if conn:
            conn.close()

def insert_image_record(weather_name: str, feeling_name: str, image_url: str) -> bool:
    """画像情報をデータベースに登録する"""
    print(f"データベース登録開始: weather='{weather_name}', feeling='{feeling_name}', url='{image_url}'")
    
    # 1. 各名称に対応するIDを取得する
    weather_id = get_id_by_exact_name("weather", "weather_name", weather_name)
    feelings_id = get_id_by_exact_name("feelings", "feeling_name", feeling_name)

    if not weather_id:
        print(f"エラー: weatherテーブルに '{weather_name}' が見つかりません。")
        return False
    if not feelings_id:
        print(f"エラー: feelingsテーブルに '{feeling_name}' が見つかりません。")
        return False

    # 2. データベースに接続
    conn = connect_db()
    if not conn:
        return False

    # 3. imagesテーブルにINSERTするSQL
    sql = """
        INSERT INTO images (weather_id, feelings_id, image_url, created_at) 
        VALUES (%s, %s, %s, NOW())
    """
    
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (weather_id, feelings_id, image_url))
            conn.commit()  # 変更を確定する
            print("✅ データベースへの登録が成功しました。")
            return True
    except Exception as e:
        conn.rollback()  # エラーが発生した場合は変更を取り消す
        print(f"データベース登録エラー: {e}")
        return False
    finally:
        if conn:
            conn.close()