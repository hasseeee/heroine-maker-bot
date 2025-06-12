import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from PIL import Image
import io
import base64

# === 可変項目 ===

weather_dict = {
    "sunny": ("light summer dress", "sunny park with blue skies"),
    "cloudy": ("long-sleeve blouse and skirt", "cloudy city street"),
    "rainy": ("raincoat and holding an umbrella", "rainy sidewalk with reflections"),
    "snowy": ("warm winter coat and scarf", "snowy town street"),
    "windy": ("hoodie and pleated skirt", "windy field with flying leaves")
}

feeling_dict = {
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
feeling_key = random.choice(list(feeling_dict.keys()))
greet_key = random.choice(list(greeting_dict.keys()))

clothing, background = weather_dict[weather_key]
mood = feeling_key
mood_expr = feeling_dict[mood_key]
greeting_action = greeting_dict[greet_key]

# === プロンプト生成 ===
prompt = (
    f"A beautiful anime-style girl, facing the viewer and warmly greeting them with a {greeting_action}, "
    f"wearing a {clothing} in a {background}, reflecting {weather_key} weather and feeling {mood}. "
    f"Soft lighting, detailed shading, anime art style, eye contact with the viewer, {mood_expr}."
)

print("🎯 使用プロンプト:\n", prompt)

# === SeleniumでWebUIにアクセス ===

chrome_options = Options()
chrome_options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=chrome_options)

try:
    driver.get("http://127.0.0.1:7860")  # Stable Diffusion WebUI

    # ページ読み込み待ち
    time.sleep(5)

    # プロンプト入力
    prompt_box = driver.find_element(By.XPATH, '//textarea[@id="txt2img_prompt"]')
    prompt_box.clear()
    prompt_box.send_keys(prompt)

    # Generateボタンクリック
    generate_btn = driver.find_element(By.XPATH, '//button[contains(text(), "Generate")]')
    generate_btn.click()

    print("🎨 画像生成中...")

    # 画像が表示されるまで待機
    timeout = 60
    while timeout > 0:
        try:
            img_element = driver.find_element(By.XPATH, '//div[@id="txt2img_gallery"]//img')
            src = img_element.get_attribute("src")
            if src.startswith("data:image/png;base64,"):
                print("✅ 画像取得成功")
                break
        except:
            pass
        time.sleep(1)
        timeout -= 1

    # Base64画像デコード
    img_data = src.split(",")[1]
    image = Image.open(io.BytesIO(base64.b64decode(img_data)))
    filename = f"output_{weather_key}_{mood_key}_{greet_key}.png"
    image.save(filename)

    print(f"✅ 画像を保存しました: {filename}")

finally:
    driver.quit()
