from fastapi import FastAPI
from pydantic import BaseModel
import httpx
import os

app = FastAPI()

# Azure App Service のアプリ設定に登録した値
EDAMAM_APP_ID = os.getenv("EDAMAM_APP_ID")
EDAMAM_APP_KEY = os.getenv("EDAMAM_APP_KEY")

TRANSLATOR_KEY = os.getenv("TRANSLATOR_KEY")
TRANSLATOR_ENDPOINT = os.getenv("TRANSLATOR_ENDPOINT")  # 例: https://xxxxxx.cognitiveservices.azure.com/

class FoodRequest(BaseModel):
    foods: str   # 例: "鶏むね肉, ブロッコリー, 卵"

# 日本語 → 英語翻訳
async def translate_to_english(text: str):
    url = f"{TRANSLATOR_ENDPOINT}/translate?api-version=3.0&to=en"
    headers = {
        "Ocp-Apim-Subscription-Key": TRANSLATOR_KEY,
        "Content-Type": "application/json"
    }
    body = [{"text": text}]

    async with httpx.AsyncClient() as client:
        r = await client.post(url, headers=headers, json=body)
        result = r.json()

        # エラー内容を確認するための安全ガード
        if "error" in result:
            return f"TRANSLATOR_ERROR: {result['error']}"

        if not result or "translations" not in result[0]:
            return "TRANSLATOR_EMPTY"

        return result[0]["translations"][0]["text"]

# Edamam 栄養 API 呼び出し
async def fetch_nutrition(english_food: str):
    # 100g をデフォルトで付ける
    query = f"100g {english_food}"

    url = (
        "https://api.edamam.com/api/nutrition-data"
        f"?app_id={EDAMAM_APP_ID}&app_key={EDAMAM_APP_KEY}"
        f"&ingr={query}"
    )

    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        return r.json()

@app.post("/nutrition")
async def get_nutrition(data: FoodRequest):

    # 食品を分割
    food_list = [f.strip() for f in data.foods.split(",")]

    results = {}

    for food in food_list:
        # 日本語 → 英語翻訳
        english = await translate_to_english(food)

        # 栄養データ取得
        nutrition = await fetch_nutrition(english)

        results[food] = {
            "translated": english,
            "nutrition": nutrition
        }

    return {
        "foods": food_list,
        "results": results
    }

@app.get("/")
def root():
    return {"message": "food-buy-api is running"}
