from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
from fastapi import FastAPI, Request, BackgroundTasks, Header
from starlette.exceptions import HTTPException
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
import os
from typing import Optional
from datetime import datetime
from time_utils import get_time_zone, get_greeting_by_time_zone
from image_utils import get_random_image_url
from weather_scraper import scrape_weather_info 

load_dotenv()

app = FastAPI()

#画像ディレクトリの公開
app.mount("/images", StaticFiles(directory="images"), name="images")    

# 環境変数
LINE_BOT_API = LineBotApi(os.environ["CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["CHANNEL_SECRET"])
base_url = 'https://heroine-maker-bot.onrender.com'

# ルート確認用エンドポイント
@app.get("/")
def read_root():
    return {"message": "LINE Bot is running"}

# LINE Webhook用エンドポイント
@app.post("/callback")
async def callback(
    request: Request,
    background_tasks: BackgroundTasks,
    x_line_signature: str = Header(None),
):
    body = await request.body()

    try:
        background_tasks.add_task(
            handler.handle, body.decode("utf-8"), x_line_signature
        )
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    return {"status": "ok"}

@app.get("/weather/")
def read_wether(date: Optional[str] = None, city: Optional[str] = None):
    """
    日付と都市名をクエリパラメータとして受け取り、天気情報を返すエンドポイント
    
    例: /wether?date=2025-05-07&city=Tokyo
    """
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    if city is None:
        city = "東京"
    
    # 実際に天気情報をスクレイピングして取得
    weather_info = scrape_weather_info(city)
    
    # 日付情報を更新
    weather_info["date"] = date
    
    return weather_info

# メッセージイベントの処理
@handler.add(MessageEvent)
def handle_message(event):
    message_text = event.message.text.lower()

    if message_text == "おはよう":
        
        messages_to_send = []
        
        greeting_message = TextSendMessage(text="おはよう！")
        messages_to_send.append(greeting_message)

        target_city = "大阪"
        weather_info = scrape_weather_info(target_city)

         # エラーがあった場合
        if "error" in weather_info:
            weather_reply_text = f"{target_city}の天気わかんなかった。ごめん<(_ _)>"
        else:
            weather_reply_text = f"今日の{target_city}は{weather_info['weather']}だよ～。最高気温は{weather_info['temperature']['max']}℃、最低気温は{weather_info['temperature']['min']}℃！！"

        weather_message = TextSendMessage(text=weather_reply_text)
        messages_to_send.append(weather_message)

        image_url = get_random_image_url(base_url)

        if image_url is None:
            print("エラー: 'images' ディレクトリに有効な画像ファイルが見つかりませんでした。")
            # 画像なしでテキストメッセージのみを返信する
            LINE_BOT_API.reply_message(event.reply_token, greeting_message)
            return # 以降の画像関連処理はスキップ

        image_msg = ImageSendMessage(
            original_content_url=image_url,
            preview_image_url=image_url
        )

        messages_to_send.append(image_msg)

        try:
            if messages_to_send:
                LINE_BOT_API.reply_message(event.reply_token, messages_to_send)
            else:
                print("送信すべきメッセージがありませんでした。")
        except Exception as e:
            print(f"メッセージ送信中にエラーが発生しました: {e}")
            # エラー発生時のユーザーへの代替メッセージ（オプション）
            try:
                LINE_BOT_API.reply_message(event.reply_token, TextSendMessage(text="ごめんなさい、処理中にエラーが発生しました。何か問題が起きたみたいです。"))
            except Exception as inner_e:
                print(f"エラー通知メッセージの送信にも失敗しました: {inner_e}")

#仮想環境に入ってね：Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
# .\venv\Scripts\activate
# uvicorn main:app --reload
# uvicorn main:app --host   
#pip install fastapi uvicorn python-dotenv requests
# pip install line-bot-sdk