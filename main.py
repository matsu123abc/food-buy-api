import os
import re
import httpx
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
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
    foods: str


# -----------------------------
# 翻訳 API（1 食材ずつ確実に翻訳）
# -----------------------------
async def translate_to_english(text: str) -> str:
    url = f"{TRANSLATOR_ENDPOINT}/translate?api-version=3.0&to=en"

    headers = {
        "Ocp-Apim-Subscription-Key": TRANSLATOR_KEY,
        "Ocp-Apim-Subscription-Region": "japanwest",
        "Content-Type": "application/json"
    }

    body = [{"text": text}]

    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(url, headers=headers, json=body)

    return r.json()[0]["translations"][0]["text"]


# -----------------------------
# Edamam 栄養取得
# -----------------------------
async def fetch_nutrition(english_food: str):
    query = f"100g {english_food}"

    url = (
        "https://api.edamam.com/api/nutrition-data"
        f"?app_id={EDAMAM_APP_ID}"
        f"&app_key={EDAMAM_APP_KEY}"
        f"&ingr={query}"
    )

    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(url)

    return r.json()


# -----------------------------
# 栄養合計
# -----------------------------
def summarize_daily_nutrition(results: dict):
    total = {"カロリー": 0, "たんぱく質": 0, "脂質": 0, "炭水化物": 0}

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
# メイン API
# -----------------------------
@app.post("/nutrition")
async def get_nutrition(req: FoodRequest):

    # ★ 全角・半角カンマどちらでも分割
    foods = re.split(r"[、,]", req.foods)
    foods = [f.strip() for f in foods if f.strip()]

    results = {}

    for food in foods:
        # ★ 1 食材ずつ翻訳 API を呼ぶ
        english = await translate_to_english(food)

        # ★ 1 食材ずつ Edamam に投げる
        nutrition = await fetch_nutrition(english)

        results[food] = {
            "translated": english,
            "nutrition": nutrition
        }

    summary = summarize_daily_nutrition(results)

    return {"foods": foods, "results": results, "summary": summary}


# -----------------------------
# UI（HTML）
# -----------------------------
@app.get("/", response_class=HTMLResponse)
async def ui():
    return """

<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>買い物 栄養バランス分析ツール</title>

<style>
  body { font-family: sans-serif; padding: 20px; background: #f5f5f5; }

  h2 { margin-bottom: 10px; }

  .selected-box {
    background: #fff;
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 20px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  }

  .category-title {
    font-size: 20px;
    margin-top: 25px;
    margin-bottom: 10px;
  }

  .food-btn {
    display: inline-block;
    padding: 12px 18px;
    margin: 5px;
    background: #e8f0fe;
    border-radius: 10px;
    font-size: 18px;
    cursor: pointer;
    user-select: none;
  }

  .food-btn.selected {
    background: #0078ff;
    color: white;
  }

  .card {
    background: white; padding: 15px; margin-bottom: 15px;
    border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  }

  button {
    width: 100%; padding: 14px; font-size: 20px;
    border: none; background: #0078ff; color: white;
    border-radius: 8px; margin-top: 20px;
  }
</style>
</head>

<body>

<h2>買い物 栄養バランス分析ツール</h2>

<!-- 選択中の食材 -->
<div class="selected-box">
  <strong>選択中の食材：</strong>
  <span id="selected-list">なし</span>
</div>

<!-- 肉類 -->
<div class="category-title">🍖 肉類</div>
<div>
  <div class="food-btn" data-food="鶏むね肉">鶏むね肉</div>
  <div class="food-btn" data-food="牛肉">牛肉</div>
  <div class="food-btn" data-food="豚ロース">豚ロース</div>
  <div class="food-btn" data-food="ひき肉">ひき肉</div>
</div>

<!-- 野菜 -->
<div class="category-title">🥦 野菜</div>
<div>
  <div class="food-btn" data-food="ブロッコリー">ブロッコリー</div>
  <div class="food-btn" data-food="にんじん">にんじん</div>
  <div class="food-btn" data-food="ほうれん草">ほうれん草</div>
  <div class="food-btn" data-food="キャベツ">キャベツ</div>
  <div class="food-btn" data-food="玉ねぎ">玉ねぎ</div>
</div>

<!-- 卵・乳製品 -->
<div class="category-title">🥚 卵・乳製品</div>
<div>
  <div class="food-btn" data-food="卵">卵</div>
  <div class="food-btn" data-food="牛乳">牛乳</div>
  <div class="food-btn" data-food="ヨーグルト">ヨーグルト</div>
  <div class="food-btn" data-food="チーズ">チーズ</div>
</div>

<!-- 魚介 -->
<div class="category-title">🐟 魚介</div>
<div>
  <div class="food-btn" data-food="さけ">さけ</div>
  <div class="food-btn" data-food="まぐろ">まぐろ</div>
  <div class="food-btn" data-food="えび">えび</div>
  <div class="food-btn" data-food="いか">いか</div>
</div>

<!-- 豆類・大豆製品 -->
<div class="category-title">🫘 豆類・大豆製品</div>
<div>
  <div class="food-btn" data-food="納豆">納豆</div>
  <div class="food-btn" data-food="豆腐">豆腐</div>
  <div class="food-btn" data-food="おから">おから</div>
  <div class="food-btn" data-food="枝豆">枝豆</div>
</div>

<button onclick="calc()">栄養を計算する</button>

<div id="result"></div>

<script>
let selectedFoods = [];

// 食材ボタンのクリック処理
document.querySelectorAll(".food-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    const food = btn.dataset.food;

    if (selectedFoods.includes(food)) {
      selectedFoods = selectedFoods.filter(f => f !== food);
      btn.classList.remove("selected");
    } else {
      selectedFoods.push(food);
      btn.classList.add("selected");
    }

    document.getElementById("selected-list").innerText =
      selectedFoods.length ? selectedFoods.join("、") : "なし";
  });
});

async function calc() {
  if (selectedFoods.length === 0) {
    alert("食材を選択してください");
    return;
  }

  const foods = selectedFoods.join(",");

  const res = await fetch("/nutrition", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({foods})
  });

  const data = await res.json();
  const summary = data.summary;
  const results = data.results;

  let html = `
    <div class="card">
      <h3>1日の合計栄養</h3>
      <p>カロリー：${summary["カロリー"]} kcal</p>
      <p>たんぱく質：${summary["たんぱく質"]} g</p>
      <p>脂質：${summary["脂質"]} g</p>
      <p>炭水化物：${summary["炭水化物"]} g</p>
      <p>食物繊維：${summary["食物繊維"] ?? 0} g</p>
    </div>
  `;

  for (const food of Object.keys(results)) {
    const item = results[food];
    const parsed = item?.nutrition?.ingredients?.[0]?.parsed?.[0];
    const nutrients = parsed?.nutrients ?? {};

    const kcal = nutrients.ENERC_KCAL?.quantity ?? 0;
    const P = nutrients.PROCNT?.quantity ?? 0;
    const F = nutrients.FAT?.quantity ?? 0;
    const C = nutrients.CHOCDF?.quantity ?? 0;
    const Fiber = nutrients.FIBTG?.quantity ?? 0;

    html += `
      <div class="card">
        <h3>${food}（${item.translated}）</h3>
        <p>カロリー：${kcal.toFixed(1)} kcal</p>
        <p>たんぱく質：${P.toFixed(1)} g</p>
        <p>脂質：${F.toFixed(1)} g</p>
        <p>炭水化物：${C.toFixed(1)} g</p>
        <p>食物繊維：${Fiber.toFixed(1)} g</p>
      </div>
    `;
  }

  document.getElementById("result").innerHTML = html;
}
</script>

</body>
</html>

"""
