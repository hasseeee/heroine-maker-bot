# test_weather_insert.py

# 必要な部品（関数）をインポートする
from dotenv import load_dotenv
from supabase_utils import get_or_create_weather_id

def run_weather_insert_test():
    """
    天気の自動インサート機能が正しく動作するかをテストする専用の関数
    """
    print("===== 天気IDの取得/作成機能のテストを開始します =====")

    # --- ケース1: 既にデータベースに存在するはずの天気でテスト ---
    print("\n--- ケース1: 既存の天気「晴」でテスト ---")
    weather_name_1 = "晴"
    # 賢い担当者に「晴」のIDを探してもらう
    weather_id_1 = get_or_create_weather_id(weather_name_1)
    
    if weather_id_1:
        print(f"  [結果] 取得したID: {weather_id_1} (期待値: 1などの既存の数字)")
        print("  [判定] ✅ 成功！既存のIDを正しく見つけられました。")
    else:
        print("  [結果] IDが取得できませんでした。")
        print("  [判定] ❌ 失敗！既存のIDが見つけられない問題が発生しています。")


    # --- ケース2: データベースに絶対に存在しない、新しい天気でテスト ---
    print("\n--- ケース2: 新しい天気「台風一過」でテスト ---")
    weather_name_2 = "台風一過"
    # 賢い担当者に「台風一過」のIDを探してもらい、なければ作ってもらう
    weather_id_2 = get_or_create_weather_id(weather_name_2)

    if weather_id_2:
        print(f"  [結果] 取得/作成されたID: {weather_id_2} (期待値: これまで存在しなかった新しい数字)")
        print("  [判定] ✅ 成功！新しい天気をデータベースに追加し、そのIDを正しく取得できました。")
    else:
        print("  [結果] IDが取得できませんでした。")
        print("  [判定] ❌ 失敗！新しい天気を追加する機能が、やはり作動していません。")

    print("\n===== テスト終了 =====")


# このファイルが直接実行された時だけ、テスト関数を呼び出す
if __name__ == "__main__":
    # まず、.envファイルから秘密の情報を読み込む
    load_dotenv()
    # テストを実行する
    run_weather_insert_test()