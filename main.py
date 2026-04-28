from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import os
from openai import AzureOpenAI

app = FastAPI()

# ============================
# Azure OpenAI クライアント
# ============================
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

class FoodRequest(BaseModel):
    foods: str  # "鶏むね肉,ブロッコリー,卵" など

# ---------------------------------------------------------
# ★ ここに 100 食材の栄養データ（八訂）をすべて埋めます（次の返答で提供）
# ---------------------------------------------------------
FOOD_DB = {

    # --- 肉類（15 食材） ---
    "鶏むね肉": {"kcal": 120.0, "protein": 22.5, "fat": 2.6, "carb": 0.0, "fiber": 0.0},
    "鶏もも肉": {"kcal": 200.0, "protein": 16.6, "fat": 14.2, "carb": 0.0, "fiber": 0.0},
    "ささみ":   {"kcal": 105.0, "protein": 23.9, "fat": 0.8, "carb": 0.0, "fiber": 0.0},
    "鶏皮":     {"kcal": 513.0, "protein": 9.0,  "fat": 50.0, "carb": 0.1, "fiber": 0.0},

    "豚ロース": {"kcal": 263.0, "protein": 19.3, "fat": 19.2, "carb": 0.2, "fiber": 0.0},
    "豚バラ":   {"kcal": 386.0, "protein": 14.2, "fat": 34.6, "carb": 0.1, "fiber": 0.0},
    "豚もも":   {"kcal": 183.0, "protein": 20.5, "fat": 10.2, "carb": 0.2, "fiber": 0.0},
    "豚ひき肉": {"kcal": 221.0, "protein": 17.7, "fat": 16.1, "carb": 0.2, "fiber": 0.0},

    "牛もも":   {"kcal": 209.0, "protein": 21.2, "fat": 12.0, "carb": 0.3, "fiber": 0.0},
    "牛肩ロース": {"kcal": 318.0, "protein": 17.7, "fat": 26.4, "carb": 0.3, "fiber": 0.0},
    "牛バラ":   {"kcal": 371.0, "protein": 14.4, "fat": 32.9, "carb": 0.3, "fiber": 0.0},
    "牛ひき肉": {"kcal": 224.0, "protein": 17.7, "fat": 16.0, "carb": 0.3, "fiber": 0.0},

    "ハム":     {"kcal": 116.0, "protein": 16.5, "fat": 4.1, "carb": 1.5, "fiber": 0.0},
    "ベーコン": {"kcal": 405.0, "protein": 12.9, "fat": 39.1, "carb": 1.0, "fiber": 0.0},
    "ソーセージ": {"kcal": 321.0, "protein": 12.0, "fat": 28.0, "carb": 3.0, "fiber": 0.0},

    # --- 魚介類（20 食材） ---
    "鮭（サーモン）": {"kcal": 133.0, "protein": 22.5, "fat": 4.5, "carb": 0.1, "fiber": 0.0},
    "サバ":           {"kcal": 202.0, "protein": 20.7, "fat": 13.8, "carb": 0.3, "fiber": 0.0},
    "アジ":           {"kcal": 121.0, "protein": 20.7, "fat": 4.5,  "carb": 0.1, "fiber": 0.0},
    "イワシ":         {"kcal": 217.0, "protein": 19.8, "fat": 15.4, "carb": 0.3, "fiber": 0.0},
    "ブリ":           {"kcal": 257.0, "protein": 21.4, "fat": 17.6, "carb": 0.3, "fiber": 0.0},

    "タラ":           {"kcal": 77.0,  "protein": 17.6, "fat": 0.5,  "carb": 0.1, "fiber": 0.0},
    "カレイ":         {"kcal": 95.0,  "protein": 18.0, "fat": 2.0,  "carb": 0.1, "fiber": 0.0},
    "ヒラメ":         {"kcal": 125.0, "protein": 20.0, "fat": 4.5,  "carb": 0.1, "fiber": 0.0},
    "マグロ赤身":     {"kcal": 125.0, "protein": 26.4, "fat": 1.4,  "carb": 0.1, "fiber": 0.0},
    "マグロ中トロ":   {"kcal": 344.0, "protein": 20.0, "fat": 27.5, "carb": 0.1, "fiber": 0.0},

    "エビ":           {"kcal": 82.0,  "protein": 18.4, "fat": 0.6,  "carb": 0.7, "fiber": 0.0},
    "イカ":           {"kcal": 88.0,  "protein": 17.9, "fat": 1.2,  "carb": 0.4, "fiber": 0.0},
    "タコ":           {"kcal": 76.0,  "protein": 16.4, "fat": 0.7,  "carb": 0.7, "fiber": 0.0},
    "ホタテ":         {"kcal": 72.0,  "protein": 13.5, "fat": 0.9,  "carb": 3.5, "fiber": 0.0},
    "しじみ":         {"kcal": 51.0,  "protein": 6.0,  "fat": 1.0,  "carb": 3.7, "fiber": 0.0},

    "アサリ":         {"kcal": 30.0,  "protein": 5.4,  "fat": 0.4,  "carb": 1.4, "fiber": 0.0},
    "サンマ":         {"kcal": 310.0, "protein": 18.5, "fat": 25.6, "carb": 0.3, "fiber": 0.0},
    "ニシン":         {"kcal": 258.0, "protein": 18.0, "fat": 20.0, "carb": 0.3, "fiber": 0.0},
    "カツオ":         {"kcal": 114.0, "protein": 25.8, "fat": 0.5,  "carb": 0.1, "fiber": 0.0},
    "うなぎ":         {"kcal": 293.0, "protein": 17.1, "fat": 23.0, "carb": 0.1, "fiber": 0.0},

    # --- 野菜（25 食材） ---
    "キャベツ":       {"kcal": 23.0, "protein": 1.3, "fat": 0.2, "carb": 5.2, "fiber": 1.8},
    "レタス":         {"kcal": 12.0, "protein": 0.6, "fat": 0.1, "carb": 2.8, "fiber": 1.1},
    "白菜":           {"kcal": 14.0, "protein": 0.8, "fat": 0.1, "carb": 3.0, "fiber": 1.0},
    "ほうれん草":     {"kcal": 20.0, "protein": 2.2, "fat": 0.4, "carb": 3.1, "fiber": 2.8},
    "小松菜":         {"kcal": 14.0, "protein": 1.5, "fat": 0.2, "carb": 2.4, "fiber": 1.9},

    "ブロッコリー":   {"kcal": 34.0, "protein": 2.8, "fat": 0.4, "carb": 6.6, "fiber": 2.6},
    "カリフラワー":   {"kcal": 27.0, "protein": 2.6, "fat": 0.2, "carb": 5.2, "fiber": 2.3},
    "にんじん":       {"kcal": 36.0, "protein": 0.7, "fat": 0.2, "carb": 8.7, "fiber": 2.8},
    "玉ねぎ":         {"kcal": 37.0, "protein": 1.0, "fat": 0.1, "carb": 8.8, "fiber": 1.5},
    "じゃがいも":     {"kcal": 76.0, "protein": 1.6, "fat": 0.1, "carb": 17.6, "fiber": 1.3},

    "さつまいも":     {"kcal": 132.0, "protein": 1.2, "fat": 0.2, "carb": 31.9, "fiber": 2.3},
    "大根":           {"kcal": 18.0, "protein": 0.5, "fat": 0.1, "carb": 4.1, "fiber": 1.3},
    "ごぼう":         {"kcal": 65.0, "protein": 1.8, "fat": 0.1, "carb": 15.4, "fiber": 5.7},
    "れんこん":       {"kcal": 66.0, "protein": 1.9, "fat": 0.1, "carb": 15.5, "fiber": 2.0},
    "たけのこ":       {"kcal": 26.0, "protein": 3.6, "fat": 0.2, "carb": 4.5, "fiber": 2.8},

    "ピーマン":       {"kcal": 22.0, "protein": 0.9, "fat": 0.2, "carb": 5.1, "fiber": 1.9},
    "パプリカ":       {"kcal": 22.0, "protein": 0.9, "fat": 0.2, "carb": 5.3, "fiber": 1.5},
    "なす":           {"kcal": 22.0, "protein": 1.0, "fat": 0.1, "carb": 5.1, "fiber": 2.2},
    "きゅうり":       {"kcal": 14.0, "protein": 1.0, "fat": 0.1, "carb": 3.0, "fiber": 1.1},
    "トマト":         {"kcal": 20.0, "protein": 0.7, "fat": 0.1, "carb": 4.7, "fiber": 1.0},

    "ミニトマト":     {"kcal": 30.0, "protein": 1.0, "fat": 0.1, "carb": 7.2, "fiber": 1.4},
    "もやし":         {"kcal": 14.0, "protein": 1.7, "fat": 0.1, "carb": 2.6, "fiber": 1.3},
    "長ねぎ":         {"kcal": 28.0, "protein": 1.3, "fat": 0.1, "carb": 6.5, "fiber": 2.2},
    "にら":           {"kcal": 21.0, "protein": 2.0, "fat": 0.3, "carb": 4.4, "fiber": 2.7},
    "生姜":           {"kcal": 30.0, "protein": 0.9, "fat": 0.3, "carb": 6.6, "fiber": 2.1},

    # --- 果物（10 食材） ---
    "りんご":       {"kcal": 56.0, "protein": 0.2, "fat": 0.1, "carb": 14.3, "fiber": 1.9},
    "バナナ":       {"kcal": 93.0, "protein": 1.1, "fat": 0.2, "carb": 22.5, "fiber": 1.1},
    "みかん":       {"kcal": 45.0, "protein": 0.6, "fat": 0.2, "carb": 11.3, "fiber": 1.0},
    "いちご":       {"kcal": 34.0, "protein": 0.9, "fat": 0.1, "carb": 8.5,  "fiber": 1.4},
    "ぶどう":       {"kcal": 59.0, "protein": 0.4, "fat": 0.1, "carb": 15.7, "fiber": 0.5},

    "梨":           {"kcal": 43.0, "protein": 0.2, "fat": 0.1, "carb": 11.0, "fiber": 1.9},
    "柿":           {"kcal": 60.0, "protein": 0.4, "fat": 0.2, "carb": 16.0, "fiber": 1.6},
    "スイカ":       {"kcal": 37.0, "protein": 0.6, "fat": 0.1, "carb": 9.5,  "fiber": 0.3},
    "メロン":       {"kcal": 42.0, "protein": 0.8, "fat": 0.1, "carb": 10.4, "fiber": 0.4},
    "パイナップル": {"kcal": 51.0, "protein": 0.5, "fat": 0.1, "carb": 13.7, "fiber": 1.5},

    # --- 豆類・大豆製品（10 食材） ---
    "木綿豆腐":     {"kcal": 72.0, "protein": 6.6, "fat": 3.5, "carb": 2.0, "fiber": 0.4},
    "絹ごし豆腐":   {"kcal": 56.0, "protein": 4.9, "fat": 3.0, "carb": 1.7, "fiber": 0.3},
    "厚揚げ":       {"kcal": 150.0, "protein": 10.0, "fat": 10.7, "carb": 3.4, "fiber": 0.5},
    "油揚げ":       {"kcal": 386.0, "protein": 23.4, "fat": 30.8, "carb": 1.4, "fiber": 0.3},
    "納豆":         {"kcal": 200.0, "protein": 16.5, "fat": 10.0, "carb": 12.1, "fiber": 6.7},

    "おから":       {"kcal": 111.0, "protein": 6.1, "fat": 3.6, "carb": 13.8, "fiber": 11.5},
    "ゆで大豆":     {"kcal": 176.0, "protein": 14.8, "fat": 9.0, "carb": 8.4, "fiber": 6.8},
    "枝豆":         {"kcal": 135.0, "protein": 11.5, "fat": 6.2, "carb": 8.8, "fiber": 5.0},
    "きな粉":       {"kcal": 437.0, "protein": 36.7, "fat": 23.5, "carb": 28.5, "fiber": 18.1},
    "豆乳（無調整）": {"kcal": 46.0, "protein": 3.6, "fat": 2.0, "carb": 3.1, "fiber": 0.2},


    # --- 乳製品・卵（10 食材） ---
    "牛乳":           {"kcal": 61.0,  "protein": 3.3,  "fat": 3.8,  "carb": 4.8,  "fiber": 0.0},
    "低脂肪乳":       {"kcal": 46.0,  "protein": 3.8,  "fat": 1.0,  "carb": 5.2,  "fiber": 0.0},
    "無脂肪乳":       {"kcal": 34.0,  "protein": 3.6,  "fat": 0.1,  "carb": 5.0,  "fiber": 0.0},
    "ヨーグルト（無糖）": {"kcal": 62.0,  "protein": 3.6,  "fat": 3.0,  "carb": 5.0,  "fiber": 0.0},
    "ヨーグルト（加糖）": {"kcal": 95.0,  "protein": 3.6,  "fat": 2.9,  "carb": 14.0, "fiber": 0.0},

    "プロセスチーズ": {"kcal": 356.0, "protein": 22.7, "fat": 27.4, "carb": 1.3,  "fiber": 0.0},
    "カッテージチーズ": {"kcal": 98.0,  "protein": 13.3, "fat": 4.3,  "carb": 2.0,  "fiber": 0.0},
    "バター":         {"kcal": 745.0, "protein": 0.5,  "fat": 82.0, "carb": 0.2,  "fiber": 0.0},
    "生クリーム":     {"kcal": 433.0, "protein": 2.0,  "fat": 45.0, "carb": 3.0,  "fiber": 0.0},
    "卵":             {"kcal": 143.0, "protein": 12.6, "fat": 9.5,  "carb": 0.7,  "fiber": 0.0},

    # --- 主食（米・パン・麺）（10 食材） ---
    "白ご飯":         {"kcal": 168.0, "protein": 2.5, "fat": 0.3, "carb": 37.1, "fiber": 0.3},
    "玄米ご飯":       {"kcal": 165.0, "protein": 2.8, "fat": 1.0, "carb": 34.2, "fiber": 1.4},
    "食パン":         {"kcal": 248.0, "protein": 8.9, "fat": 4.4, "carb": 43.4, "fiber": 2.3},
    "ロールパン":     {"kcal": 313.0, "protein": 9.7, "fat": 8.6, "carb": 49.4, "fiber": 2.1},
    "クロワッサン":   {"kcal": 406.0, "protein": 8.2, "fat": 21.0, "carb": 45.0, "fiber": 2.0},

    "うどん（ゆで）": {"kcal": 105.0, "protein": 2.6, "fat": 0.4, "carb": 21.6, "fiber": 0.9},
    "そば（ゆで）":   {"kcal": 132.0, "protein": 4.8, "fat": 1.0, "carb": 24.0, "fiber": 2.0},
    "パスタ（ゆで）": {"kcal": 149.0, "protein": 5.8, "fat": 0.9, "carb": 28.8, "fiber": 1.8},
    "中華麺（ゆで）": {"kcal": 149.0, "protein": 5.0, "fat": 1.0, "carb": 28.0, "fiber": 1.0},
    "餅":             {"kcal": 235.0, "protein": 4.0, "fat": 0.5, "carb": 50.3, "fiber": 0.5},

}
# ---------------------------------------------------------

def summarize_from_db(selected: list[str]):
    total = {
        "カロリー": 0.0,
        "たんぱく質": 0.0,
        "脂質": 0.0,
        "炭水化物": 0.0,
        "食物繊維": 0.0,
        "糖質": 0.0,
    }

    results = {}

    for name in selected:
        name = name.strip()
        if not name or name not in FOOD_DB:
            continue

        d = FOOD_DB[name]
        sugar = d["carb"] - d["fiber"]

        results[name] = {
            "kcal": d["kcal"],
            "protein": d["protein"],
            "fat": d["fat"],
            "carb": d["carb"],
            "fiber": d["fiber"],
            "sugar": sugar,
        }

        total["カロリー"]   += d["kcal"]
        total["たんぱく質"] += d["protein"]
        total["脂質"]       += d["fat"]
        total["炭水化物"]   += d["carb"]
        total["食物繊維"]   += d["fiber"]
        total["糖質"]       += sugar

    for k in total:
        total[k] = round(total[k], 1)

    return results, total

@app.post("/nutrition")
async def nutrition(req: FoodRequest):
    foods = req.foods.split(",")
    results, summary = summarize_from_db(foods)
    return JSONResponse({"results": results, "summary": summary})


# -----------------------------
# AI コメント生成（SerpAPI ニュース版）
# -----------------------------
@app.post("/ai_analysis")
async def ai_analysis(data: dict):
    summary = data["summary"]

    prompt = f"""
あなたはプロの栄養士です。
以下は、ユーザーが選択した食材（すべて100g換算）の合計栄養です。

【合計栄養】
- カロリー: {summary["カロリー"]} kcal
- たんぱく質: {summary["たんぱく質"]} g
- 脂質: {summary["脂質"]} g
- 炭水化物: {summary["炭水化物"]} g
- 食物繊維: {summary["食物繊維"]} g
- 糖質: {summary["糖質"]} g

以下を日本語で出力してください：

### 1. 栄養バランス総合スコア（100点満点）
（点数のみ）

### 2. 良い点
（箇条書きで3つ）

### 3. 改善点
（箇条書きで3つ）

### 4. 総合コメント
（短く、わかりやすく）
"""

    res = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=800
    )

    return {"analysis": res.choices[0].message.content.strip()}


# ---------------------------------------------------------
# ★ ここから HTML + JS を返すエンドポイント
# ---------------------------------------------------------
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

  .info-note {
    font-size: 16px;
    color: #555;
    margin-bottom: 15px;
  }

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
<div class="info-note">※ すべて100g換算で計算しています</div>

<div class="selected-box">
  <strong>選択中の食材：</strong>
  <span id="selected-list">なし</span>
</div>

<!-- ▼▼▼ 食材カテゴリ（100 食材版） ▼▼▼ -->
（※ 章さんの食材ボタン部分はそのまま残してください）
<!-- ▲▲▲ 食材カテゴリ ▲▲▲ -->

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

  let html = \`
    <div class="card">
      <h3>1日の合計栄養（100g換算）</h3>
      <p>カロリー：\${summary["カロリー"]} kcal</p>
      <p>たんぱく質：\${summary["たんぱく質"]} g</p>
      <p>脂質：\${summary["脂質"]} g</p>
      <p>炭水化物：\${summary["炭水化物"]} g</p>
      <p>食物繊維：\${summary["食物繊維"]} g</p>
      <p>糖質：\${summary["糖質"]} g</p>
    </div>
  \`;

  for (const food of Object.keys(results)) {
    const item = results[food];

    html += \`
      <div class="card">
        <h3>\${food}（100g）</h3>
        <p>カロリー：\${item.kcal.toFixed(1)} kcal</p>
        <p>たんぱく質：\${item.protein.toFixed(1)} g</p>
        <p>脂質：\${item.fat.toFixed(1)} g</p>
        <p>炭水化物：\${item.carb.toFixed(1)} g</p>
        <p>食物繊維：\${item.fiber.toFixed(1)} g</p>
        <p>糖質：\${item.sugar.toFixed(1)} g</p>
      </div>
    \`;
  }

  /* ▼▼▼ AI 栄養分析 ▼▼▼ */
  const aiRes = await fetch("/ai_analysis", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ summary })
  });

  const aiData = await aiRes.json();

  html += \`
    <div class="card">
      <h3>AI 栄養分析</h3>
      <div>\${aiData.analysis.replace(/\\n/g, "<br>")}</div>
    </div>
  \`;
  /* ▲▲▲ AI 栄養分析 ▲▲▲ */

  document.getElementById("result").innerHTML = html;
}
</script>

</body>
</html>
   

"""
