# run_tests.py

from dotenv import load_dotenv
# 変更点: インポート元を 'database.py' ファイルに変更
from supabase_utils import (
    get_weather_id_by_name,
    get_feelings_id,
    get_image_url
)

# .envファイルを読み込み、環境変数を設定する
# database.py内の関数がこれを使う
load_dotenv()

def run_tests():
    """作成した各関数をテストする"""
    print("===== データベース連携関数のテストを開始します =====")

    # --- 1. get_weather_id_by_name のテスト ---
    print("\n--- 1. 天気名からIDを取得する関数のテスト ---")
    weather_name_1 = "晴れ"
    weather_id_1 = get_weather_id_by_name(weather_name_1)
    print(f"'{weather_name_1}' のID: {weather_id_1}  (期待値: 1など数字)")

    # データベースにないはずのデータでテスト
    weather_name_2 = "火山"
    weather_id_2 = get_weather_id_by_name(weather_name_2)
    print(f"'{weather_name_2}' のID: {weather_id_2}  (期待値: None)")
    
    # 元のコードのロジックをテスト（「曇り」が「曇りのち晴れ」に含まれるか）
    weather_name_3 = "今日の天気は曇りのち晴れ"
    weather_id_3 = get_weather_id_by_name(weather_name_3)
    print(f"'{weather_name_3}' のID: {weather_id_3}  (期待値: '曇り'のIDなど数字)")


    # --- 2. get_feelings_id のテスト ---
    print("\n--- 2. ランダムなFeelingsのIDを取得する関数のテスト ---")
    random_feelings_id = get_feelings_id()
    print(f"取得したランダムなFeelings ID: {random_feelings_id}  (期待値: 1, 2など数字)")
    if random_feelings_id is None:
        print("  => [注意] feelingsテーブルにデータがないか、接続に問題があるかもしれません。")

    # --- 3. get_image_url のテスト ---
    print("\n--- 3. 天気IDとFeelings IDから画像URLを取得する関数のテスト ---")

    # ケース3-1: 存在するIDの組み合わせ（例: 晴れ & 元気）
    # ※あなたのDBのIDに合わせて数字を変更してください
    weather_id_ok = 1 
    feelings_id_ok = 1 
    image_url_1 = get_image_url(weather_id_ok, feelings_id_ok)
    print(f"天気ID:{weather_id_ok}, Feelings ID:{feelings_id_ok} の場合...")
    print(f"  取得したURL: {image_url_1}  (期待値: httpから始まるURL文字列)")
    if image_url_1 is None:
        print("  => [注意] imagesテーブルにこの組み合わせのデータがないかもしれません。")
        
    # ケース3-2: 存在しないIDの組み合わせ
    weather_id_ng = 999
    feelings_id_ng = 999
    image_url_2 = get_image_url(weather_id_ng, feelings_id_ng)
    print(f"天気ID:{weather_id_ng}, Feelings ID:{feelings_id_ng} の場合...")
    print(f"  取得したURL: {image_url_2}  (期待値: None)")

    print("\n===== テスト終了 =====")


# このファイルが直接実行された時だけ、run_tests()関数を呼び出す
if __name__ == "__main__":
    run_tests()