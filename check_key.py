from dotenv import load_dotenv
import os

load_dotenv()

loaded_key = os.environ.get("SUPABASE_KEY")

print("--- 環境変数キーの確認 ---")
if loaded_key:
    # セキュリティのため、キーの最後の6文字だけ表示します
    print(f"読み込まれたSUPABASE_KEYの末尾: ...{loaded_key[-6:]}")
    print("これがあなたの service_role キーの末尾と一致しているか確認してください。")
else:
    print("SUPABASE_KEYが読み込めていませんでした。")
print("--------------------------")