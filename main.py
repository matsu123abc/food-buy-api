from fastapi import FastAPI
from pydantic import BaseModel
import httpx
import os

app = FastAPI()

EDAMAM_APP_ID = os.getenv("EDAMAM_APP_ID")
EDAMAM_APP_KEY = os.getenv("EDAMAM_APP_KEY")

class FoodRequest(BaseModel):
    foods: str   # 例: "chicken breast, broccoli, egg"

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

    food_list = [f.strip() for f in data.foods.split(",")]

    results = {}

    for food in food_list:
        nutrition = await fetch_nutrition(food)
        results[food] = {"nutrition": nutrition}

    return {
        "foods": food_list,
        "results": results
    }

@app.get("/")
def root():
    return {"message": "food-buy-api is running"}
