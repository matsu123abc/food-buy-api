import os
import httpx
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# -----------------------------
# 環境変数
# -----------------------------
TRANSLATOR_KEY = os.getenv("TRANSLATOR_KEY")
TRANSLATOR_ENDPOINT = os.getenv("TRANSLATOR_ENDPOINT")
EDAMAM_APP_ID = os.getenv("EDAMAM_APP_ID")
EDAMAM_APP_KEY = os.getenv("EDAMAM_APP_KEY")

# -----------------------------
# 入力モデル
# -----------------------------
class FoodRequest(BaseModel):
    foods: str  # カンマ区切りの食品名


# -----------------------------
# 翻訳処理
# -----------------------------
async def translate_to_english(text: str) -> str:
    url = f"{TRANSLATOR_ENDPOINT}/translate?api-version=3.0&to=en"

    headers = {
        "Ocp-Apim-Subscription-Key": TRANSLATOR_KEY,
        "Ocp-Apim-Subscription-Region": "japanwest",  # ★重要
        "Content-Type": "application/json"
    }

    body = [{"text": text}]

    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(url, headers=headers, json=body)

    try:
        return r.json()[0]["translations"][0]["text"]
    except:
        return f"TRANSLATOR_ERROR: {r.text}"


# -----------------------------
# Edamam 栄養取得
# -----------------------------
async def fetch_nutrition(english_food: str):
    query = f"100g {english_food}"

    url = (
        "https://api.edamam.com/api/nutrition-data"
        f"?app_id={EDAMAM_APP_ID}&app_key={EDAMAM_APP_KEY}"
        f"&ingr={query}"
    )

    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(url)

    try:
        return r.json()
    except:
        return {"error": "NOT_JSON", "content": r.text}


# -----------------------------
# 栄養合計（PFC＋カロリー）
# -----------------------------
def summarize_daily_nutrition(results: dict):
    total = {
        "calories": 0,
        "protein": 0,
        "fat": 0,
        "carbs": 0
    }

    for food, data in results.items():
        try:
            nutrients = data["nutrition"]["ingredients"][0]["parsed"][0]["nutrients"]

            total["calories"] += nutrients.get("ENERC_KCAL", {}).get("quantity", 0)
            total["protein"]  += nutrients.get("PROCNT", {}).get("quantity", 0)
            total["fat"]      += nutrients.get("FAT", {}).get("quantity", 0)
            total["carbs"]    += nutrients.get("CHOCDF", {}).get("quantity", 0)

        except:
            pass

    return total


# -----------------------------
# メインAPI：食品 → 翻訳 → 栄養 → 合計
# -----------------------------
@app.post("/nutrition")
async def get_nutrition(req: FoodRequest):
    foods = [f.strip() for f in req.foods.split(",")]

    results = {}

    for food in foods:
        english = await translate_to_english(food)
        nutrition = await fetch_nutrition(english)

        results[food] = {
            "translated": english,
            "nutrition": nutrition
        }

    # ★ 1日の合計栄養を計算
    summary = summarize_daily_nutrition(results)

    return {
        "foods": foods,
        "results": results,
        "summary": summary
    }


# -----------------------------
# 翻訳テスト用
# -----------------------------
@app.get("/translate-test")
async def translate_test(text: str):
    english = await translate_to_english(text)
    return {"original": text, "translated": english}
