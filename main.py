from fastapi import FastAPI
from pydantic import BaseModel
import httpx
import os

app = FastAPI()

# Azure App Service のアプリ設定に登録した値
EDAMAM_APP_ID = os.getenv("EDAMAM_APP_ID")
EDAMAM_APP_KEY = os.getenv("EDAMAM_APP_KEY")

class FoodRequest(BaseModel):
    foods: str   # 例: "chicken breast, broccoli, egg"

# Edamam 栄養 API 呼び出し
async def fetch_nutrition(english_food: str):
    url = (
        "https://api.edamam.com/api/nutrition-data"
        f"?app_id={EDAMAM_APP_ID}&app_key={EDAMAM_APP_KEY}"
        f"&ingr={english_food}"
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
        # 英語食品名をそのまま Edamam に送る
        nutrition = await fetch_nutrition(food)

        results[food] = {
            "nutrition": nutrition
        }

    return {
        "foods": food_list,
        "results": results
    }

@app.get("/")
def root():
    return {"message": "food-buy-api is running"}
