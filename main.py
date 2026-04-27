import os
import httpx
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI()

# -----------------------------
# 日本語 → 英語 辞書（必要に応じて追加可能）
# -----------------------------
JP_TO_EN = {
    "鶏むね肉": "chicken breast",
    "ブロッコリー": "broccoli",
    "卵": "egg",
}

# -----------------------------
# 入力モデル
# -----------------------------
class FoodRequest(BaseModel):
    foods: str  # カンマ区切りの食品名


# -----------------------------
# 辞書変換（翻訳 API 不使用）
# -----------------------------
def translate_to_english_local(text: str) -> str:
    return JP_TO_EN.get(text, text)


# -----------------------------
# Edamam 栄養取得
# -----------------------------
async def fetch_nutrition(english_food: str):
    query = f"100g {english_food}"

    url = (
        "https://api.edamam.com/api/nutrition-data"
        f"?app_id={os.getenv('EDAMAM_APP_ID')}"
        f"&app_key={os.getenv('EDAMAM_APP_KEY')}"
        f"&ingr={query}"
    )

    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(url)

    return r.json()


# -----------------------------
# 栄養合計（日本語 summary）
# -----------------------------
def summarize_daily_nutrition(results: dict):
    total = {
        "カロリー": 0,
        "たんぱく質": 0,
        "脂質": 0,
        "炭水化物": 0
    }

    for food, data in results.items():
        try:
            nutrients = data["nutrition"]["ingredients"][0]["parsed"][0]["nutrients"]

            total["カロリー"] += nutrients.get("ENERC_KCAL", {}).get("quantity", 0)
            total["たんぱく質"] += nutrients.get("PROCNT", {}).get("quantity", 0)
            total["脂質"]     += nutrients.get("FAT", {}).get("quantity", 0)
            total["炭水化物"] += nutrients.get("CHOCDF", {}).get("quantity", 0)

        except:
            pass

    return total


# -----------------------------
# メインAPI：食品 → 辞書変換 → 栄養 → 合計
# -----------------------------
@app.post("/nutrition")
async def get_nutrition(req: FoodRequest):
    foods = [f.strip() for f in req.foods.split(",")]

    results = {}

    for food in foods:
        # ★ 辞書変換（翻訳 API 不使用）
        english = translate_to_english_local(food)

        # ★ 1 食材ずつ Edamam に投げる
        nutrition = await fetch_nutrition(english)

        results[food] = {
            "translated": english,
            "nutrition": nutrition
        }

    summary = summarize_daily_nutrition(results)

    return {
        "foods": foods,
        "results": results,
        "summary": summary
    }


# -----------------------------
# UI（HTML）統合
# -----------------------------
@app.get("/", response_class=HTMLResponse)
async def ui():
    return """
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>栄養計算ツール</title>
<style>
  body { font-family: sans-serif; padding: 20px; background: #f5f5f5; }
  .card {
    background: white; padding: 15px; margin-bottom: 15px;
    border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  }
  button {
    width: 100%; padding: 12px; font-size: 18px;
    border: none; background: #0078ff; color: white;
    border-radius: 8px; margin-top: 10px;
  }
  input {
    width: 100%; padding: 12px; font-size: 18px;
    border-radius: 8px; border: 1px solid #ccc;
  }
</style>
</head>
<body>

<h2>栄養計算ツール</h2>

<div class="card">
  <label>食品名（カンマ区切り）</label>
  <input id="foods" placeholder="鶏むね肉, ブロッコリー, 卵">
  <button onclick="calc()">計算する</button>
</div>

<div id="result"></div>

<script>
async function calc() {
  const foods = document.getElementById("foods").value;

  const res = await fetch("/nutrition", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({foods})
  });

  const data = await res.json();
  const summary = data.summary;
  const results = data.results;

  // --- 合計栄養カード ---
  let html = `
    <div class="card">
      <h3>1日の合計栄養</h3>
      <p>カロリー：${summary["カロリー"]} kcal</p>
      <p>たんぱく質：${summary["たんぱく質"]} g</p>
      <p>脂質：${summary["脂質"]} g</p>
      <p>炭水化物：${summary["炭水化物"]} g</p>
    </div>
  `;

  // --- 食材ごとの Result をそのまま表示 ---
  for (const food of Object.keys(results)) {
    const item = results[food];

    html += `
      <div class="card">
        <h3>${food}</h3>
        <pre style="white-space: pre-wrap; font-size: 12px;">
${JSON.stringify(item, null, 2)}
        </pre>
      </div>
    `;
  }

  document.getElementById("result").innerHTML = html;
}
</script>

</body>
</html>
"""
