from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
from fastapi import FastAPI, Request, BackgroundTasks, Header
from starlette.exceptions import HTTPException
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
import os
import requests #weahter
from bs4 import BeautifulSoup
from pprint import pprint
from typing import Optional
from datetime import datetime
from time_utils import get_time_zone, get_greeting_by_time_zone
from image_utils import get_random_image_url

load_dotenv()

app = FastAPI()

#画像ディレクトリの公開
app.mount("/images", StaticFiles(directory="images"), name="images")    

# 環境変数
LINE_BOT_API = LineBotApi(os.environ["CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["CHANNEL_SECRET"])
base_url = os.environ.get("BASE_URL", "http://localhost:8000")

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


def scrape_weather_info(city: str):
    """
    天気情報をスクレイピングする関数
    
    Args:
        city (str): 都市名 (デフォルトは東京)
    
    Returns:
        dict: 天気情報を含む辞書
    """
    try:
        # 都市名とtenki.jpの対応するURLパラメータのマッピング
        city_url_mapping = {
            "東京": "3/16/4410/13113",  # 東京・千代田区
            "大阪": "6/30/6200/27100",  # 大阪・大阪市
            "名古屋": "5/26/5110/23100",  # 愛知・名古屋市
            "福岡": "9/47/8210/40130",  # 福岡・福岡市
            "札幌": "1/2/1400/01100",  # 北海道・札幌市
            "仙台": "2/9/3410/04100",  # 宮城・仙台市
            "広島": "7/34/6710/34100",  # 広島・広島市
            "神戸": "6/30/6200/28110",  # 兵庫・神戸市
            "京都": "6/29/6110/26100",  # 京都・京都市
            "横浜": "3/17/4610/14100",  # 神奈川・横浜市
        }
        
        # 都市名に基づいてURLを生成
        url_param = city_url_mapping.get(city, "3/16/4410/13113")  # デフォルトは東京
        url = f"https://tenki.jp/forecast/{url_param}/"
        
        # リクエストを送信
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # エラーチェック
        
        # BeautifulSoupでHTMLを解析
        soup = BeautifulSoup(response.content, "html.parser")
        
        # 天気情報の抽出
        today_forecast = soup.select_one(".forecast-days-wrap .today-weather")
        if today_forecast:
            weather_text = today_forecast.select_one(".weather-telop").text.strip() if today_forecast.select_one(".weather-telop") else "不明"
            
            # 気温の取得
            temp_high = today_forecast.select_one(".high-temp .value").text.strip() if today_forecast.select_one(".high-temp .value") else "不明"
            temp_low = today_forecast.select_one(".low-temp .value").text.strip() if today_forecast.select_one(".low-temp .value") else "不明"
            
            # 降水確率の取得
            precip_prob = []
            precip_rows = today_forecast.select(".precip-table tbody tr")
            if precip_rows:
                for row in precip_rows[1:2]:  # 2行目（降水確率）を取得
                    for cell in row.select("td"):
                        precip_prob.append(cell.text.strip())
            
            # 結果の辞書を作成
            weather_info = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "city": city,
                "weather": weather_text,
                "temperature": {
                    "max": temp_high,
                    "min": temp_low
                },
                "precipitation_probability": precip_prob if precip_prob else ["--", "--", "--", "--"],
                "source": "tenki.jp"
            }
            return weather_info
        else:
            return {"error": "天気情報を取得できませんでした", "city": city} 
    except Exception as e:
        return {"error": f"スクレイピングエラー: {str(e)}", "city": city}


@app.get("/wether/")
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

        LINE_BOT_API.reply_message(event.reply_token, messages_to_send,)


#仮想環境に入ってね：Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
# .\venv\Scripts\activate
# uvicorn main:app --reload
# uvicorn main:app --host   
#pip install fastapi uvicorn python-dotenv requests
# pip install line-bot-sdk