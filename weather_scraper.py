import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Optional

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
            "東京": "3/16/4410/13113",    # 東京・千代田区
            "大阪": "6/30/6200/27100",    # 大阪・大阪市
            "名古屋": "5/26/5110/23100",    # 愛知・名古屋市
            "福岡": "9/47/8210/40130",    # 福岡・福岡市
            "札幌": "1/2/1400/01100",    # 北海道・札幌市
            "仙台": "2/9/3410/04100",    # 宮城・仙台市
            "広島": "7/34/6710/34100",    # 広島・広島市
            "神戸": "6/30/6200/28110",    # 兵庫・神戸市
            "京都": "6/29/6110/26100",    # 京都・京都市
            "横浜": "3/17/4610/14100",    # 神奈川・横浜市
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

# FastAPIのエンドポイントはmain.pyに残すため、このファイルからは削除
# @app.get("/wether/") 関数はmain.pyに残します。