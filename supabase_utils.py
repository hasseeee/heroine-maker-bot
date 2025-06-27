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

def get_or_create_weather_id(weather_name: str) -> int | None:
    """天気名を含むレコードのIDをSQLで直接取得する"""
    conn = connect_db()
    if not conn:
        return None

    # SQLインジェクションを防ぐため、プレースホルダ(%s)を使用
    sql = "SELECT id FROM weather WHERE weather_name = %s"

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
                print(f"既存の天気に '{weather_name}' が見つかりませんでした。追加します。")
                sql_insert = "INSERT INTO weather (weather_name) VALUES (%s) RETURNING id"
                cur.execute(sql_insert, (weather_name,))
                new_id = cur.fetchone()[0]
                conn.commit()  # ここで変更を確定
                print(f"✅ 新しい天気ID: {new_id} として登録しました。")
                return new_id
                
    except Exception as e:
        if conn:
            conn.rollback() # エラーが起きたら変更を取り消す
        print(f"Error in get_or_create_weather_id: {e}")
        return None
    finally:
        if conn:
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
    weather_id = get_or_create_weather_id(current_weather_text)
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
    def is_safe_name(s: str) -> bool:
        # 文字が英数字またはアンダースコアのみで構成されているかチェック
        return all(c.isalnum() or c == '_' for c in s)

    if not is_safe_name(table_name) or not is_safe_name(column_name):
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

def insert_image_record(weather_name: str, feelings_name: str, image_url: str, prompt: str) -> bool:
    """画像情報をデータベースに登録する"""
    print(f"データベース登録開始: weather='{weather_name}', feeling='{feelings_name}', url='{image_url}'")
    
    # 1. 各名称に対応するIDを取得する
    weather_id = get_id_by_exact_name("weather", "weather_name", weather_name)
    feelings_id = get_id_by_exact_name("feelings", "feelings_name", feelings_name)

    if not weather_id:
        print(f"エラー: weatherテーブルに '{weather_name}' が見つかりません。")
        return False
    if not feelings_id:
        print(f"エラー: feelingsテーブルに '{feelings_name}' が見つかりません。")
        return False

    # 2. データベースに接続
    conn = connect_db()
    if not conn:
        return False

    # 3. imagesテーブルにINSERTするSQL
    sql = """
        INSERT INTO images (weather_id, feelings_id, prompt, image_url) 
        VALUES (%s, %s, %s, %s)
    """
    
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (weather_id, feelings_id, prompt, image_url))
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
            
def get_image_url_for_bot(weather_name: str) -> tuple[str | None, int | None, int | None]:
    """
    天気名をもとに、必要なIDを全て取得・作成し、最終的な画像URLを返す
    一度の接続で全ての処理を完結させるための専用関数
    戻り値: (画像URL, 天気ID, 気分ID)
    """
    conn = None
    try:
        conn = connect_db()
        if not conn:
            return None, None, None

        with conn.cursor() as cur:
            # 1. 天気IDを取得、なければ作成
            weather_id = None
            sql_weather = "SELECT id FROM weather WHERE TRIM(weather_name) = %s"
            cur.execute(sql_weather, (weather_name,))
            result_weather = cur.fetchone()
            if result_weather:
                weather_id = result_weather[0]
            else:
                sql_insert_weather = "INSERT INTO weather (weather_name) VALUES (%s) RETURNING id"
                cur.execute(sql_insert_weather, (weather_name,))
                weather_id = cur.fetchone()[0]
                conn.commit()

            # 2. ランダムな気分IDを取得
            sql_feelings = "SELECT id FROM feelings ORDER BY RANDOM() LIMIT 1"
            cur.execute(sql_feelings)
            result_feelings = cur.fetchone()
            feelings_id = result_feelings[0] if result_feelings else None

            # 3. 取得したIDを使って画像URLを取得
            image_url = None
            if weather_id and feelings_id:
                sql_image = "SELECT image_url FROM images WHERE weather_id = %s AND feelings_id = %s ORDER BY RANDOM() LIMIT 1"
                cur.execute(sql_image, (weather_id, feelings_id))
                result_image = cur.fetchone()
                image_url = result_image[0] if result_image else None
            
            return image_url, weather_id, feelings_id

    except Exception as e:
        if conn: conn.rollback()
        print(f"Error in get_image_url_for_bot: {e}")
        return None, None, None
    finally:
        if conn: conn.close()