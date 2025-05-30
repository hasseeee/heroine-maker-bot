from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
from fastapi import FastAPI, Request, BackgroundTasks, Header
from starlette.exceptions import HTTPException
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
import os
import random

load_dotenv()

app = FastAPI()

app.mount("/images", StaticFiles(directory="images"), name="images")    

# 環境変数
LINE_BOT_API = LineBotApi(os.environ["CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["CHANNEL_SECRET"])

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

# メッセージイベントの処理
@handler.add(MessageEvent)
def handle_message(event):
    message_text = event.message.text.lower()

    if message_text == "おはよう":
        reply = TextSendMessage(text="おはよう！")
        images_dir = os.path.join(os.path.dirname(__file__), "images")
        
        # 対象の画像拡張子
        valid_extensions = (".jpg", ".jpeg", ".png", ".gif", ".webp")
        
        # 画像ファイルだけを抽出
        image_files = [
            f for f in os.listdir(images_dir)
            if f.lower().endswith(valid_extensions)
        ]

        # ランダム選択
        chosen_image = random.choice(image_files)

        # 画像URL（RenderのURLに合わせて修正）
        image_url = f"https://heroine-maker-bot.onrender.com/images/{chosen_image}"

        image_msg = ImageSendMessage(
            original_content_url=image_url,
            preview_image_url=image_url
        )

        LINE_BOT_API.reply_message(event.reply_token, reply)
