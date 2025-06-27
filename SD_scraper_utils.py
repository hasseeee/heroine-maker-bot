import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from PIL import Image
import io
import base64
import os
from dotenv import load_dotenv

# supabase_utilsから新しい関数をインポート
from supabase_utils import insert_image_record

load_dotenv()

# === 可変項目 ===

weather_dict = {
    "sunny": ("light summer dress", "sunny park with blue skies"),
    "cloudy": ("long-sleeve blouse and skirt", "cloudy city street"),
    "rainy": ("raincoat and holding an umbrella", "rainy sidewalk with reflections"),
    "snowy": ("warm winter coat and scarf", "snowy town street"),
    "windy": ("hoodie and pleated skirt", "windy field with flying leaves")
}

feelings_dict = {
    "energetic": "bright smile",
    "neutral": "soft smile",
    "sleepy": "gentle sleepy eyes",
    "calm": "calm eyes",
    "wistful": "soft eyes and slight smile"
}

greeting_dict = {
    "wave": "gentle wave",
    "raise_hand": "raising one hand to greet",
    "say_good_morning": "smiling and saying 'Good morning'",
    "bow": "bowing slightly in greeting",
    "cheerful_wave": "cheerfully waving and saying 'Good morning!'"
}

# === ランダム選択 ===
weather_key = random.choice(list(weather_dict.keys()))
feeling_key = random.choice(list(feelings_dict.keys()))
greet_key = random.choice(list(greeting_dict.keys()))

clothing, background = weather_dict[weather_key]
mood = feeling_key
mood_expr = feelings_dict[feeling_key]
greeting_action = greeting_dict[greet_key]

# === 英語キーと日本語（DB登録名）を紐付ける翻訳辞書 ===
weather_en_to_jp = {
    "sunny": "晴れ",
    "cloudy": "曇り",
    "rainy": "雨",
    "snowy": "雪",
    "windy": "風" 
}

feeling_en_to_jp = {
    "energetic": "元気",
    "neutral": "ふつう",
    "sleepy": "眠い",
    "calm": "穏やか",
    "wistful": "物思い"
}

# === ランダム選択 ===
weather_key = random.choice(list(weather_dict.keys()))
feeling_key = random.choice(list(feelings_dict.keys()))
greet_key = random.choice(list(greeting_dict.keys()))

clothing, background = weather_dict[weather_key]
mood = feeling_key # moodは英語キーのままプロンプト生成に使用
mood_expr = feelings_dict[feeling_key]
greeting_action = greeting_dict[greet_key]

# === プロンプト生成 ===
prompt = (
    f"A beautiful anime-style girl, facing the viewer and warmly greeting them with a {greeting_action}, "
    f"wearing a {clothing} in a {background}, reflecting {weather_key} weather and feeling {mood}. "
    f"Soft lighting, detailed shading, anime art style, eye contact with the viewer, {mood_expr}."
)

print("🎯 使用プロンプト:\n", prompt)

# === FastAPIのベースURLと画像保存先ディレクトリ ===
BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8000") # .envから取得、なければデフォルト値
SAVE_DIRECTORY = r"D:\products\heroine-maker-bot\generate_images" 

# === SeleniumでWebUIにアクセス ===

chrome_options = Options()
chrome_options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=chrome_options)

try:
    driver.get("http://127.0.0.1:7860")  # Stable Diffusion WebUI

    # ▼▼▼ time.sleep(5) をより確実な待機方法に変更 ▼▼▼
    print("🖥️ Stable Diffusion Web UIのページ読み込みを待っています...")
    
    # 最大30秒間、プロンプト入力欄が表示されるまで待機する
    wait = WebDriverWait(driver, 30)
    prompt_box = wait.until(EC.presence_of_element_located((By.XPATH, '//textarea[@data-testid="textbox"]')))
    
    print("✅ プロンプト入力欄を発見しました。")

    # プロンプト入力
    prompt_box = driver.find_element(By.XPATH, '//textarea[@data-testid="textbox"]')
    prompt_box.clear()
    prompt_box.send_keys(prompt)

    # Generateボタンクリック
    generate_btn = driver.find_element(By.XPATH, '//button[@id="txt2img_generate"]')
    generate_btn.click()

    print("🎨 画像生成中...")

    # 画像が表示されるまで待機
    wait = WebDriverWait(driver, 120) 
    
    img_element_xpath = '//div[@id="txt2img_gallery"]//img'
    img_element = wait.until(EC.presence_of_element_located((By.XPATH, img_element_xpath)))

    wait.until(lambda d: d.find_element(By.XPATH, img_element_xpath).get_attribute("src").startswith("data:image/png;base64,"))

    src = img_element.get_attribute("src")
    print("✅ 画像取得成功")

    # Base64画像デコード
    img_data = src.split(",")[1]
    image = Image.open(io.BytesIO(base64.b64decode(img_data)))

    # 保存先ディレクトリが存在しない場合は作成
    if not os.path.exists(SAVE_DIRECTORY):
        os.makedirs(SAVE_DIRECTORY)
    
    # ファイル名を作成（タイムスタンプでダブりを防ぐ）
    timestamp = int(time.time())
    filename = f"heroine_{weather_key}_{feeling_key}_{timestamp}.png"
    save_path = os.path.join(SAVE_DIRECTORY, filename)
    image.save(filename)

    print(f"✅ 画像を保存しました: {save_path}")

    # === ここからデータベース登録処理 ===
    # 公開用のURLを組み立てる
    public_image_url = f"{BASE_URL}/{SAVE_DIRECTORY}/{filename}"

    # 翻訳辞書を使って、DB登録用の日本語名を取得
    weather_jp_name = weather_en_to_jp.get(weather_key)
    feeling_jp_name = feeling_en_to_jp.get(feeling_key)

    if weather_jp_name and feeling_jp_name:
    # データベースに登録
    # feeling_key は mood と同じなので mood を使用
        success = insert_image_record(weather_jp_name, feeling_jp_name, public_image_url)
        if not success:
            print("❌ データベース登録に失敗しました。")
    else:
        print("❌ 翻訳辞書にキーが見つからなかったため、DB登録をスキップしました。")

finally:
    driver.quit()
