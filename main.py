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
    total = {
        "カロリー": 0,
        "たんぱく質": 0,
        "脂質": 0,
        "炭水化物": 0,
        "食物繊維": 0,   # ★ 追加
    }

    for food, data in results.items():
        try:
            nutrients = data["nutrition"]["ingredients"][0]["parsed"][0]["nutrients"]

            total["カロリー"] += nutrients.get("ENERC_KCAL", {}).get("quantity", 0)
            total["たんぱく質"] += nutrients.get("PROCNT", {}).get("quantity", 0)
            total["脂質"]     += nutrients.get("FAT", {}).get("quantity", 0)
            total["炭水化物"] += nutrients.get("CHOCDF", {}).get("quantity", 0)
            total["食物繊維"] += nutrients.get("FIBTG", {}).get("quantity", 0)  # ★ 追加
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

  .accordion {
    background: #fff;
    padding: 12px;
    margin-top: 10px;
    border-radius: 10px;
    cursor: pointer;
    font-size: 20px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  }

  .panel {
    display: none;
    padding: 10px 5px;
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

<div style="margin-bottom: 15px; font-size: 16px; color: #555;">
  ※ このツールは、すべての食材を 100g として計算しています
</div>

<!-- 選択中の食材 -->
<div class="selected-box">
  <strong>選択中の食材：</strong>
  <span id="selected-list">なし</span>
</div>

<!-- アコーディオン：カテゴリ別 -->

<div class="accordion">🍖 肉類</div>
<div class="panel">
  <div class="food-btn" data-food="鶏むね肉">鶏むね肉</div>
  <div class="food-btn" data-food="鶏もも肉">鶏もも肉</div>
  <div class="food-btn" data-food="ささみ">ささみ</div>
  <div class="food-btn" data-food="豚ロース">豚ロース</div>
  <div class="food-btn" data-food="豚こま">豚こま</div>
  <div class="food-btn" data-food="豚バラ">豚バラ</div>
  <div class="food-btn" data-food="牛こま">牛こま</div>
  <div class="food-btn" data-food="牛ロース">牛ロース</div>
  <div class="food-btn" data-food="牛ひき肉">牛ひき肉</div>
  <div class="food-btn" data-food="豚ひき肉">豚ひき肉</div>
  <div class="food-btn" data-food="鶏ひき肉">鶏ひき肉</div>
  <div class="food-btn" data-food="ベーコン">ベーコン</div>
</div>

<div class="accordion">🥦 野菜</div>
<div class="panel">
  <div class="food-btn" data-food="ブロッコリー">ブロッコリー</div>
  <div class="food-btn" data-food="にんじん">にんじん</div>
  <div class="food-btn" data-food="玉ねぎ">玉ねぎ</div>
  <div class="food-btn" data-food="キャベツ">キャベツ</div>
  <div class="food-btn" data-food="ほうれん草">ほうれん草</div>
  <div class="food-btn" data-food="レタス">レタス</div>
  <div class="food-btn" data-food="トマト">トマト</div>
  <div class="food-btn" data-food="きゅうり">きゅうり</div>
  <div class="food-btn" data-food="ピーマン">ピーマン</div>
  <div class="food-btn" data-food="パプリカ">パプリカ</div>
  <div class="food-btn" data-food="じゃがいも">じゃがいも</div>
  <div class="food-btn" data-food="さつまいも">さつまいも</div>
  <div class="food-btn" data-food="大根">大根</div>
  <div class="food-btn" data-food="白菜">白菜</div>
  <div class="food-btn" data-food="小松菜">小松菜</div>
  <div class="food-btn" data-food="もやし">もやし</div>
  <div class="food-btn" data-food="なす">なす</div>
  <div class="food-btn" data-food="かぼちゃ">かぼちゃ</div>
  <div class="food-btn" data-food="ごぼう">ごぼう</div>
  <div class="food-btn" data-food="ねぎ">ねぎ</div>
  <div class="food-btn" data-food="しめじ">しめじ</div>
  <div class="food-btn" data-food="えのき">えのき</div>
  <div class="food-btn" data-food="しいたけ">しいたけ</div>
  <div class="food-btn" data-food="舞茸">舞茸</div>
  <div class="food-btn" data-food="アスパラガス">アスパラガス</div>
</div>

<div class="accordion">🥚 卵・乳製品</div>
<div class="panel">
  <div class="food-btn" data-food="卵">卵</div>
  <div class="food-btn" data-food="牛乳">牛乳</div>
  <div class="food-btn" data-food="ヨーグルト">ヨーグルト</div>
  <div class="food-btn" data-food="チーズ">チーズ</div>
  <div class="food-btn" data-food="バター">バター</div>
  <div class="food-btn" data-food="生クリーム">生クリーム</div>
  <div class="food-btn" data-food="豆乳">豆乳</div>
  <div class="food-btn" data-food="プロセスチーズ">プロセスチーズ</div>
  <div class="food-btn" data-food="カッテージチーズ">カッテージチーズ</div>
  <div class="food-btn" data-food="クリームチーズ">クリームチーズ</div>
</div>

<div class="accordion">🐟 魚介類</div>
<div class="panel">
  <div class="food-btn" data-food="さけ">さけ</div>
  <div class="food-btn" data-food="まぐろ">まぐろ</div>
  <div class="food-btn" data-food="ぶり">ぶり</div>
  <div class="food-btn" data-food="さば">さば</div>
  <div class="food-btn" data-food="いわし">いわし</div>
  <div class="food-btn" data-food="たら">たら</div>
  <div class="food-btn" data-food="えび">えび</div>
  <div class="food-btn" data-food="いか">いか</div>
  <div class="food-btn" data-food="ほたて">ほたて</div>
  <div class="food-btn" data-food="あじ">あじ</div>
  <div class="food-btn" data-food="さんま">さんま</div>
  <div class="food-btn" data-food="かつお">かつお</div>
  <div class="food-btn" data-food="しらす">しらす</div>
  <div class="food-btn" data-food="かに">かに</div>
  <div class="food-btn" data-food="たこ">たこ</div>
</div>

<div class="accordion">🫘 豆類・大豆製品</div>
<div class="panel">
  <div class="food-btn" data-food="豆腐">豆腐</div>
  <div class="food-btn" data-food="納豆">納豆</div>
  <div class="food-btn" data-food="おから">おから</div>
  <div class="food-btn" data-food="枝豆">枝豆</div>
  <div class="food-btn" data-food="厚揚げ">厚揚げ</div>
  <div class="food-btn" data-food="油揚げ">油揚げ</div>
  <div class="food-btn" data-food="ひよこ豆">ひよこ豆</div>
  <div class="food-btn" data-food="レンズ豆">レンズ豆</div>
  <div class="food-btn" data-food="黒豆">黒豆</div>
  <div class="food-btn" data-food="大豆">大豆</div>
</div>

<div class="accordion">🍎 果物</div>
<div class="panel">
  <div class="food-btn" data-food="りんご">りんご</div>
  <div class="food-btn" data-food="バナナ">バナナ</div>
  <div class="food-btn" data-food="みかん">みかん</div>
  <div class="food-btn" data-food="いちご">いちご</div>
  <div class="food-btn" data-food="ぶどう">ぶどう</div>
  <div class="food-btn" data-food="キウイ">キウイ</div>
  <div class="food-btn" data-food="パイナップル">パイナップル</div>
  <div class="food-btn" data-food="桃">桃</div>
  <div class="food-btn" data-food="梨">梨</div>
  <div class="food-btn" data-food="柿">柿</div>
  <div class="food-btn" data-food="スイカ">スイカ</div>
  <div class="food-btn" data-food="メロン">メロン</div>
</div>

<div class="accordion">🍚 穀物・パン・麺</div>
<div class="panel">
  <div class="food-btn" data-food="ごはん">ごはん</div>
  <div class="food-btn" data-food="玄米">玄米</div>
  <div class="food-btn" data-food="食パン">食パン</div>
  <div class="food-btn" data-food="ロールパン">ロールパン</div>
  <div class="food-btn" data-food="うどん">うどん</div>
  <div class="food-btn" data-food="そば">そば</div>
  <div class="food-btn" data-food="パスタ">パスタ</div>
  <div class="food-btn" data-food="オートミール">オートミール</div>
  <div class="food-btn" data-food="コーンフレーク">コーンフレーク</div>
  <div class="food-btn" data-food="ラーメン">ラーメン</div>
</div>

<div class="accordion">🍱 加工食品</div>
<div class="panel">
  <div class="food-btn" data-food="ハム">ハム</div>
  <div class="food-btn" data-food="ソーセージ">ソーセージ</div>
  <div class="food-btn" data-food="ツナ缶">ツナ缶</div>
  <div class="food-btn" data-food="コーン缶">コーン缶</div>
  <div class="food-btn" data-food="カレー">カレー</div>
  <div class="food-btn" data-food="ミートボール">ミートボール</div>
</div>

<button onclick="calc()">栄養を計算する</button>

<div id="result"></div>

<script>
let selectedFoods = [];

// アコーディオン動作
document.querySelectorAll(".accordion").forEach(acc => {
  acc.addEventListener("click", () => {
    acc.classList.toggle("active");
    const panel = acc.nextElementSibling;
    panel.style.display = panel.style.display === "block" ? "none" : "block";
  });
});

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
