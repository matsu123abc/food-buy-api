from fastapi import FastAPI
from pydantic import BaseModel
import httpx
import os

app = FastAPI()

# APIキーは App Service の「構成 → アプリケーション設定」で設定
API_KEY = os.getenv("NINJA_API_KEY")
NUTRITION_URL = "https://api.api-ninjas.com/v1/nutrition"

class FoodRequest(BaseModel):
    foods: str   # 例: "鶏むね肉, ブロッコリー, 卵"

# 栄養API呼び出し
async def fetch_nutrition(food_name: str):
    headers = {"X-Api-Key": API_KEY}
    params = {"query": food_name}

    async with httpx.AsyncClient() as client:
        r = await client.get(NUTRITION_URL, headers=headers, params=params)
        return r.json()

@app.post("/nutrition")
async def get_nutrition(data: FoodRequest):

    # 入力された食品を分割
    food_list = [f.strip() for f in data.foods.split(",")]

    results = {}

    # 食品ごとにAPIを呼び出す
    for food in food_list:
        res = await fetch_nutrition(food)
        results[food] = res

    return {
        "foods": food_list,
        "nutrition": results
    }

@app.get("/")
def root():
    return {"message": "food-buy-api is running"}
