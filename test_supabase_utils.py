from dotenv import load_dotenv
# 変更点: get_random_mood_id -> get_feelings_mood_id に変更
from supabase_utils import (
    get_weather_id_by_name,
    get_feelings_id,
    get_image_url
)

# .envファイルを読み込んで、Supabaseに接続できるようにする
load_dotenv()

def run_tests():
    """作成した各関数をテストする"""
    print("===== Supabase連携関数のテストを開始します =====")

    # --- 1. get_weather_id_by_name のテスト (変更なし) ---
    print("\n--- 1. 天気名からIDを取得する関数のテスト ---")
    weather_name_1 = "晴れ"
    weather_id_1 = get_weather_id_by_name(weather_name_1)
    print(f"'{weather_name_1}' のID: {weather_id_1}  (期待値: 1など数字)")

    weather_name_3 = "火山"
    weather_id_3 = get_weather_id_by_name(weather_name_3)
    print(f"'{weather_name_3}' のID: {weather_id_3}  (期待値: None)")

    # --- 2. get_feelings_mood_id のテスト ---
    # 変更点: 関数名と説明を修正
    print("\n--- 2. ランダムなFeelingsのIDを取得する関数のテスト ---")
    random_feelings_id = get_feelings_id()
    print(f"取得したランダムなFeelings ID: {random_feelings_id}  (期待値: 1, 2など数字)")
    if random_feelings_id is None:
        print("  => [注意] feelingsテーブルにデータがないか、接続に問題があるかもしれません。")

    # --- 3. get_image_url のテスト ---
    # 変更点: 引数名と説明を修正
    print("\n--- 3. 天気IDとFeelings IDから画像URLを取得する関数のテスト ---")

    # ケース3-1: 存在するIDの組み合わせ（晴れ & 元気）
    # ※あなたのDBのIDに合わせて数字を変更してください
    weather_id_ok = 1 
    feelings_id_ok = 1 # 変数名を feeling_id_ok に変更
    image_url_1 = get_image_url(weather_id_ok, feelings_id_ok) # 引数を変更
    print(f"天気ID:{weather_id_ok}, Feelings ID:{feelings_id_ok} の場合...") # 説明を修正
    print(f"  取得したURL: {image_url_1}  (期待値: httpから始まるURL文字列)")
    if image_url_1 is None:
        print("  => [注意] imagesテーブルにこの組み合わせのデータがないかもしれません。")
        
    # ケース3-2: 存在しないIDの組み合わせ
    weather_id_ng = 999
    feelings_id_ng = 999
    image_url_2 = get_image_url(weather_id_ng, feelings_id_ng) # 引数を変更
    print(f"天気ID:{weather_id_ng}, Feelings ID:{feelings_id_ng} の場合...") # 説明を修正
    print(f"  取得したURL: {image_url_2}  (期待値: None)")

    print("\n===== テスト終了 =====")


if __name__ == "__main__":
    run_tests()