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

#画像ディレクトリの公開
app.mount("/images", StaticFiles(directory="images"), name="images")    

# 環境変数
LINE_BOT_API = LineBotApi(os.environ["CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["CHANNEL_SECRET"])

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

# メッセージイベントの処理
@handler.add(MessageEvent)
def handle_message(event):
    message_text = event.message.text.lower()

    if message_text == "おはよう":
        reply = TextSendMessage(text="おはよう！")

        base_url = "https://heroine-maker-bot.onrender.com"

        image_url = get_random_image_url(base_url)

        if image_url is None:
            print("エラー: 'images' ディレクトリに有効な画像ファイルが見つかりませんでした。")
            # 画像なしでテキストメッセージのみを返信する
            LINE_BOT_API.reply_message(event.reply_token, reply)
            return # 以降の画像関連処理はスキップ

        image_msg = ImageSendMessage(
            original_content_url=image_url,
            preview_image_url=image_url
        )

        messages_to_send = [reply, image_msg]
        LINE_BOT_API.reply_message(event.reply_token, messages_to_send)
