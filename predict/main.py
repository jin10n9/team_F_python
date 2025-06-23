import requests
import pandas as pd
import joblib
from collections import defaultdict
from datetime import datetime
import os
import logging
import json
import azure.functions as func

API_KEY = os.getenv("AZURE_API_KEY")

model_files = [
    '黒ビール(本)_model.pkl',
    'フルーツビール(本)_model.pkl',
    'ペールエール(本)_model.pkl',
    'ホワイトビール(本)_model.pkl',
    'ラガー(本)_model.pkl',
    'ペールエール(本)_model.pkl'
]

weekday_ja = {
    "Monday": "曜日_月",
    "Tuesday": "曜日_火",
    "Wednesday": "曜日_水",
    "Thursday": "曜日_木",
    "Friday": "曜日_金",
    "Saturday": "曜日_土",
    "Sunday": "日"
}

def get_weather(lat, lon, api_key, units="metric", lang="ja"):
    base_url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": units,
        "lang": lang
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        daily_data = defaultdict(lambda: {"temps": [], "rains": [], "weather_18h": ""})
        for entry in data.get("list", []):
            dt_txt = entry.get("dt_txt", "")
            time_part = dt_txt[-8:]
            date_part = dt_txt[:10]

            if time_part in ["18:00:00", "21:00:00"]:
                temp = entry["main"]["temp"]
                rain = entry.get("rain", {}).get("3h", 0.0)
                daily_data[date_part]["temps"].append(temp)
                daily_data[date_part]["rains"].append(rain)

        result_list = []
        for date, info in sorted(daily_data.items()):
            if len(info["temps"]) == 2:
                date_obj = datetime.strptime(date, "%Y-%m-%d")
                weekday_en = date_obj.strftime("%A")
                weekday = weekday_ja.get(weekday_en, "")
                avg_temp = sum(info["temps"]) / 2
                avg_rain = sum(info["rains"]) / 2

                result_list.append({
                    "date": date,
                    "曜日": weekday,
                    "平均気温": round(avg_temp, 1),
                    "降水量": round(avg_rain, 1)
                })

        return result_list

    except requests.exceptions.RequestException as e:
        logging.error(f"天気取得エラー: {e}")
        return []

def predict_sales(lat=35.6895, lon=139.692):
    data = get_weather(lat, lon, API_KEY)
    df = pd.DataFrame(data)
    df = df[df['曜日'] != '日']

    df_onehot = pd.get_dummies(df, columns=['曜日'])
    feature_cols = ['平均気温', '降水量', '曜日_月', '曜日_火', '曜日_水', '曜日_木', '曜日_金', '曜日_土']

    for col in feature_cols:
        if col not in df_onehot.columns:
            df_onehot[col] = 0

    X_future = df_onehot[feature_cols]

    results_list = []
    for model_file in model_files:
        model_name = model_file.replace('_model.pkl', '')
        model = joblib.load(os.path.join(os.getcwd(), model_file))
        predicted_sales = model.predict(X_future)

        for day, pred in zip(df['曜日'], predicted_sales):
            results_list.append({
                'モデル名': model_name,
                '曜日': day,
                '予測値': round(float(pred), 2)
            })

    return results_list

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        prediction = predict_sales()
        result = {"predicted_sales": prediction}
        return func.HttpResponse(
            json.dumps(result, ensure_ascii=False, indent=4),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        error_result = {"error": str(e)}
        return func.HttpResponse(
            json.dumps(error_result, ensure_ascii=False),
            mimetype="application/json",
            status_code=500
        )
