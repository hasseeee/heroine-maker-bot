from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from PIL import Image
import io
import base64
import os

# --- 設定 ---
prompt_text = "A beautiful anime-style girl, facing the viewer and warmly greeting them with a gentle wave, wearing a light summer dress in a sunny park with blue skies, reflecting sunny weather and feeling energetic. Soft lighting, detailed shading, anime art style, eye contact with the viewer, bright smile."

# --- Chrome起動オプション ---
options = Options()
options.add_argument("--start-maximized")

# ChromeDriverのパス（自動検出できる場合は不要）
driver = webdriver.Chrome(options=options)

try:
    # Stable Diffusion WebUI にアクセス
    driver.get("http://127.0.0.1:7860")

    # テキストエリアが表示されるまで待機
    time.sleep(5)

    # --- プロンプト入力 ---
    prompt_box = driver.find_element(By.XPATH, '//textarea[@id="txt2img_prompt"]')
    prompt_box.clear()
    prompt_box.send_keys(prompt_text)

    # --- 生成ボタンクリック（「Generate」ボタン） ---
    generate_btn = driver.find_element(By.XPATH, '//button[contains(text(), "Generate")]')
    generate_btn.click()

    print("🎨 画像生成中...")

    # --- 画像が生成されるまで待機（最大60秒） ---
    timeout = 60
    while timeout > 0:
        try:
            img_element = driver.find_element(By.XPATH, '//div[@id="txt2img_gallery"]//img')
            src = img_element.get_attribute("src")
            if src.startswith("data:image/png;base64,"):
                print("✅ 画像検出")
                break
        except:
            pass
        time.sleep(1)
        timeout -= 1

    # --- 画像デコードして保存 ---
    img_data = src.split(",")[1]
    image = Image.open(io.BytesIO(base64.b64decode(img_data)))
    output_path = "output_scraped.png"
    image.save(output_path)

    print(f"✅ 画像を保存しました: {output_path}")

finally:
    driver.quit()