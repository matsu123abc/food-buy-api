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
class AIRequest(BaseModel):
    summary: dict
    foods: list
    details: dict

@app.post("/ai_analysis")
async def ai_analysis(data: AIRequest):

    summary = data.summary
    foods = data.foods
    details = data.details

    prompt = f"""
あなたはプロの栄養士兼、買い物アドバイザーです。
以下のデータをもとに、総合的な栄養分析と買い物アドバイスを行ってください。

### 1. 合計栄養の分析（summary）
{summary}

### 2. 選択された食材（foods）
{foods}

### 3. 食材ごとの栄養詳細（details）
{details}

---

### 出力フォーマット（必ずこの形式で出力）

### 1. 栄養バランス総合スコア（100点満点）
数値だけ

### 2. 良い点
- 箇条書きで3〜5個

### 3. 改善点
- 箇条書きで3〜5個

### 4. 食材ごとの特徴まとめ
- 食材名：特徴（高たんぱく、ビタミン豊富、低脂質など）

### 5. 組み合わせの評価
- 栄養的に良い点
- 改善できる点

### 6. 追加購入アドバイス
- 不足栄養素を補うための具体的な食材を提案

### 7. 総合コメント
短くわかりやすくまとめる
"""

    # OpenAI API 呼び出し
    res = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=800
    )

    analysis_text = res.choices[0].message.content.strip()

    return JSONResponse({"analysis": analysis_text})

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

<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>買い物 栄養バランス分析ツール</title>

<style>
  body { font-family: sans-serif; padding: 20px; background: #f5f5f5; }
  h2 { margin-bottom: 10px; }
  .info-note { font-size: 16px; color: #555; margin-bottom: 15px; }
  .selected-box {
    background: #fff; padding: 10px; border-radius: 10px;
    margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  }
  .category-title { font-size: 20px; margin-top: 25px; margin-bottom: 10px; }
  .food-row {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    margin: 4px 0;
  }
  .food-btn {
    display: inline-block; padding: 10px 14px; margin: 3px 8px 3px 0;
    background: #e8f0fe; border-radius: 10px; font-size: 16px;
    cursor: pointer; user-select: none;
  }
  .food-btn.selected { background: #0078ff; color: white; }
  .amount-select {
    font-size: 14px;
    padding: 4px 6px;
    border-radius: 6px;
    margin: 3px 0;
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
  /* スマホ縦画面（幅480px以下）で文字とボタンをさらに大きく */
  @media (max-width: 480px) {

      body {
          font-size: 22px !important;
      }

      summary {
          font-size: 26px !important;
          padding: 12px 0 !important;
      }

      .food-row {
          margin: 12px 0 !important;
      }

      .food-btn {
          font-size: 22px !important;
          padding: 18px 22px !important;
          border-radius: 12px !important;
      }

      .amount-select {
          font-size: 22px !important;
          padding: 10px 14px !important;
      }

      #selected-list {
          font-size: 22px !important;
      }
  }

</style>
</head>

<body>

<h2>買い物 栄養バランス分析ツール</h2>
<div class="info-note">※ すべて100g換算で計算し、「数量」で倍率をかけています</div>

<div class="selected-box">
  <strong>選択中の食材：</strong>
  <span id="selected-list">なし</span>
</div>

<details>
  <summary>🍖 肉類（15）</summary>

  <div class="food-row">
    <div class="food-btn" data-food="鶏むね肉">鶏むね肉</div>
    <select class="amount-select" data-food="鶏むね肉">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="鶏もも肉">鶏もも肉</div>
    <select class="amount-select" data-food="鶏もも肉">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="ささみ">ささみ</div>
    <select class="amount-select" data-food="ささみ">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="鶏皮">鶏皮</div>
    <select class="amount-select" data-food="鶏皮">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="豚ロース">豚ロース</div>
    <select class="amount-select" data-food="豚ロース">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="豚バラ">豚バラ</div>
    <select class="amount-select" data-food="豚バラ">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="豚もも">豚もも</div>
    <select class="amount-select" data-food="豚もも">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="豚ひき肉">豚ひき肉</div>
    <select class="amount-select" data-food="豚ひき肉">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="牛もも">牛もも</div>
    <select class="amount-select" data-food="牛もも">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="牛肩ロース">牛肩ロース</div>
    <select class="amount-select" data-food="牛肩ロース">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="牛バラ">牛バラ</div>
    <select class="amount-select" data-food="牛バラ">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="牛ひき肉">牛ひき肉</div>
    <select class="amount-select" data-food="牛ひき肉">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="ハム">ハム</div>
    <select class="amount-select" data-food="ハム">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="ベーコン">ベーコン</div>
    <select class="amount-select" data-food="ベーコン">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="ソーセージ">ソーセージ</div>
    <select class="amount-select" data-food="ソーセージ">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

</details>

<details>
  <summary>🐟 魚介類（20）</summary>

  <div class="food-row">
    <div class="food-btn" data-food="鮭（サーモン）">鮭（サーモン）</div>
    <select class="amount-select" data-food="鮭（サーモン）">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="サバ">サバ</div>
    <select class="amount-select" data-food="サバ">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="アジ">アジ</div>
    <select class="amount-select" data-food="アジ">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="イワシ">イワシ</div>
    <select class="amount-select" data-food="イワシ">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="ブリ">ブリ</div>
    <select class="amount-select" data-food="ブリ">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="タラ">タラ</div>
    <select class="amount-select" data-food="タラ">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="カレイ">カレイ</div>
    <select class="amount-select" data-food="カレイ">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="ヒラメ">ヒラメ</div>
    <select class="amount-select" data-food="ヒラメ">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="マグロ赤身">マグロ赤身</div>
    <select class="amount-select" data-food="マグロ赤身">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="マグロ中トロ">マグロ中トロ</div>
    <select class="amount-select" data-food="マグロ中トロ">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="エビ">エビ</div>
    <select class="amount-select" data-food="エビ">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="イカ">イカ</div>
    <select class="amount-select" data-food="イカ">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="タコ">タコ</div>
    <select class="amount-select" data-food="タコ">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="ホタテ">ホタテ</div>
    <select class="amount-select" data-food="ホタテ">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="しじみ">しじみ</div>
    <select class="amount-select" data-food="しじみ">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="アサリ">アサリ</div>
    <select class="amount-select" data-food="アサリ">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="サンマ">サンマ</div>
    <select class="amount-select" data-food="サンマ">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="ニシン">ニシン</div>
    <select class="amount-select" data-food="ニシン">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="カツオ">カツオ</div>
    <select class="amount-select" data-food="カツオ">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="うなぎ">うなぎ</div>
    <select class="amount-select" data-food="うなぎ">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

</details>

<details>
  <summary>🥬 野菜（25）</summary>

  <div class="food-row">
    <div class="food-btn" data-food="キャベツ">キャベツ</div>
    <select class="amount-select" data-food="キャベツ">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="レタス">レタス</div>
    <select class="amount-select" data-food="レタス">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="白菜">白菜</div>
    <select class="amount-select" data-food="白菜">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="ほうれん草">ほうれん草</div>
    <select class="amount-select" data-food="ほうれん草">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="小松菜">小松菜</div>
    <select class="amount-select" data-food="小松菜">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="ブロッコリー">ブロッコリー</div>
    <select class="amount-select" data-food="ブロッコリー">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="カリフラワー">カリフラワー</div>
    <select class="amount-select" data-food="カリフラワー">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="にんじん">にんじん</div>
    <select class="amount-select" data-food="にんじん">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="玉ねぎ">玉ねぎ</div>
    <select class="amount-select" data-food="玉ねぎ">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="じゃがいも">じゃがいも</div>
    <select class="amount-select" data-food="じゃがいも">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="さつまいも">さつまいも</div>
    <select class="amount-select" data-food="さつまいも">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="大根">大根</div>
    <select class="amount-select" data-food="大根">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="ごぼう">ごぼう</div>
    <select class="amount-select" data-food="ごぼう">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="れんこん">れんこん</div>
    <select class="amount-select" data-food="れんこん">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="たけのこ">たけのこ</div>
    <select class="amount-select" data-food="たけのこ">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="ピーマン">ピーマン</div>
    <select class="amount-select" data-food="ピーマン">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="パプリカ">パプリカ</div>
    <select class="amount-select" data-food="パプリカ">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="なす">なす</div>
    <select class="amount-select" data-food="なす">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="きゅうり">きゅうり</div>
    <select class="amount-select" data-food="きゅうり">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="トマト">トマト</div>
    <select class="amount-select" data-food="トマト">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="ミニトマト">ミニトマト</div>
    <select class="amount-select" data-food="ミニトマト">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="もやし">もやし</div>
    <select class="amount-select" data-food="もやし">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="長ねぎ">長ねぎ</div>
    <select class="amount-select" data-food="長ねぎ">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="にら">にら</div>
    <select class="amount-select" data-food="にら">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="生姜">生姜</div>
    <select class="amount-select" data-food="生姜">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

</details>

<details>
  <summary>🍎 果物（10）</summary>

  <div class="food-row">
    <div class="food-btn" data-food="りんご">りんご</div>
    <select class="amount-select" data-food="りんご">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="バナナ">バナナ</div>
    <select class="amount-select" data-food="バナナ">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="みかん">みかん</div>
    <select class="amount-select" data-food="みかん">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="いちご">いちご</div>
    <select class="amount-select" data-food="いちご">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="ぶどう">ぶどう</div>
    <select class="amount-select" data-food="ぶどう">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="梨">梨</div>
    <select class="amount-select" data-food="梨">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="柿">柿</div>
    <select class="amount-select" data-food="柿">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="スイカ">スイカ</div>
    <select class="amount-select" data-food="スイカ">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="メロン">メロン</div>
    <select class="amount-select" data-food="メロン">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="パイナップル">パイナップル</div>
    <select class="amount-select" data-food="パイナップル">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

</details>

<details>
  <summary>🌱 豆類・大豆製品（10）</summary>

  <div class="food-row">
    <div class="food-btn" data-food="木綿豆腐">木綿豆腐</div>
    <select class="amount-select" data-food="木綿豆腐">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="絹ごし豆腐">絹ごし豆腐</div>
    <select class="amount-select" data-food="絹ごし豆腐">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="厚揚げ">厚揚げ</div>
    <select class="amount-select" data-food="厚揚げ">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="油揚げ">油揚げ</div>
    <select class="amount-select" data-food="油揚げ">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="納豆">納豆</div>
    <select class="amount-select" data-food="納豆">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="おから">おから</div>
    <select class="amount-select" data-food="おから">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="ゆで大豆">ゆで大豆</div>
    <select class="amount-select" data-food="ゆで大豆">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="枝豆">枝豆</div>
    <select class="amount-select" data-food="枝豆">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="きな粉">きな粉</div>
    <select class="amount-select" data-food="きな粉">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="豆乳（無調整）">豆乳（無調整）</div>
    <select class="amount-select" data-food="豆乳（無調整）">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

</details>

<details>
  <summary>🥚 乳製品・卵（10）</summary>

  <div class="food-row">
    <div class="food-btn" data-food="牛乳">牛乳</div>
    <select class="amount-select" data-food="牛乳">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="低脂肪乳">低脂肪乳</div>
    <select class="amount-select" data-food="低脂肪乳">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="無脂肪乳">無脂肪乳</div>
    <select class="amount-select" data-food="無脂肪乳">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="ヨーグルト（無糖）">ヨーグルト（無糖）</div>
    <select class="amount-select" data-food="ヨーグルト（無糖）">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="ヨーグルト（加糖）">ヨーグルト（加糖）</div>
    <select class="amount-select" data-food="ヨーグルト（加糖）">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="プロセスチーズ">プロセスチーズ</div>
    <select class="amount-select" data-food="プロセスチーズ">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="カッテージチーズ">カッテージチーズ</div>
    <select class="amount-select" data-food="カッテージチーズ">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="バター">バター</div>
    <select class="amount-select" data-food="バター">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="生クリーム">生クリーム</div>
    <select class="amount-select" data-food="生クリーム">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="卵">卵</div>
    <select class="amount-select" data-food="卵">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

</details>

<details>
  <summary>🍚 主食（10）</summary>

  <div class="food-row">
    <div class="food-btn" data-food="白ご飯">白ご飯</div>
    <select class="amount-select" data-food="白ご飯">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="玄米ご飯">玄米ご飯</div>
    <select class="amount-select" data-food="玄米ご飯">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="食パン">食パン</div>
    <select class="amount-select" data-food="食パン">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="ロールパン">ロールパン</div>
    <select class="amount-select" data-food="ロールパン">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="クロワッサン">クロワッサン</div>
    <select class="amount-select" data-food="クロワッサン">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="うどん（ゆで）">うどん（ゆで）</div>
    <select class="amount-select" data-food="うどん（ゆで）">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="そば（ゆで）">そば（ゆで）</div>
    <select class="amount-select" data-food="そば（ゆで）">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="パスタ（ゆで）">パスタ（ゆで）</div>
    <select class="amount-select" data-food="パスタ（ゆで）">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="中華麺（ゆで）">中華麺（ゆで）</div>
    <select class="amount-select" data-food="中華麺（ゆで）">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

  <div class="food-row">
    <div class="food-btn" data-food="餅">餅</div>
    <select class="amount-select" data-food="餅">
      <option value="1">1（100g）</option>
      <option value="0.5">0.5（50g）</option>
      <option value="1.5">1.5（150g）</option>
      <option value="2">2（200g）</option>
      <option value="3">3（300g）</option>
    </select>
  </div>

</details>

<button onclick="calc()">栄養を計算する</button>

<div id="result"></div>

<button id="recipe-btn">レシピを提案する</button>

<div class="card" style="margin-top: 15px;">
  <label for="recipe-style">料理ジャンル：</label>
  <select id="recipe-style">
    <option value="和食">和食</option>
    <option value="洋食">洋食</option>
    <option value="中華">中華</option>
  </select>
</div>

<div id="recipe-result" class="card"></div>

<script>
let selectedFoods = [];

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

  // 食材ごとの数量（100g単位）を取得
  let amounts = {};
  document.querySelectorAll(".amount-select").forEach(sel => {
    const food = sel.dataset.food;
    const value = parseFloat(sel.value);
    amounts[food] = value;
  });

  const foods = selectedFoods.join(",");

  const res = await fetch("/nutrition", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({foods})
  });

  const data = await res.json();
  const baseSummary = data.summary;
  const baseResults = data.results;

  // 量を反映した実際の栄養値を計算
  let adjustedResults = {};
  let adjustedSummary = {
    "カロリー": 0,
    "たんぱく質": 0,
    "脂質": 0,
    "炭水化物": 0,
    "食物繊維": 0,
    "糖質": 0
  };

  for (const food of Object.keys(baseResults)) {
    const item = baseResults[food];
    const amount = amounts[food] || 1; // デフォルト1（100g）

    const adj = {
      kcal: item.kcal * amount,
      protein: item.protein * amount,
      fat: item.fat * amount,
      carb: item.carb * amount,
      fiber: item.fiber * amount,
      sugar: item.sugar * amount
    };

    adjustedResults[food] = adj;

    adjustedSummary["カロリー"]   += adj.kcal;
    adjustedSummary["たんぱく質"] += adj.protein;
    adjustedSummary["脂質"]       += adj.fat;
    adjustedSummary["炭水化物"]   += adj.carb;
    adjustedSummary["食物繊維"]   += adj.fiber;
    adjustedSummary["糖質"]       += adj.sugar;
  }

  for (const k in adjustedSummary) {
    adjustedSummary[k] = Number(adjustedSummary[k].toFixed(1));
  }

  let html = "";
  html += '<div class="card">';
  html += '<h3>合計栄養（数量反映後）</h3>';
  html += '<p>カロリー：' + adjustedSummary["カロリー"] + ' kcal</p>';
  html += '<p>たんぱく質：' + adjustedSummary["たんぱく質"] + ' g</p>';
  html += '<p>脂質：' + adjustedSummary["脂質"] + ' g</p>';
  html += '<p>炭水化物：' + adjustedSummary["炭水化物"] + ' g</p>';
  html += '<p>食物繊維：' + adjustedSummary["食物繊維"] + ' g</p>';
  html += '<p>糖質：' + adjustedSummary["糖質"] + ' g</p>';
  html += '</div>';

  for (const food of Object.keys(adjustedResults)) {
    const item = adjustedResults[food];

    html += '<div class="card">';
    html += '<h3>' + food + '（数量反映後）</h3>';
    html += '<p>カロリー：' + item.kcal.toFixed(1) + ' kcal</p>';
    html += '<p>たんぱく質：' + item.protein.toFixed(1) + ' g</p>';
    html += '<p>脂質：' + item.fat.toFixed(1) + ' g</p>';
    html += '<p>炭水化物：' + item.carb.toFixed(1) + ' g</p>';
    html += '<p>食物繊維：' + item.fiber.toFixed(1) + ' g</p>';
    html += '<p>糖質：' + item.sugar.toFixed(1) + ' g</p>';
    html += '</div>';
  }

  const aiRes = await fetch("/ai_analysis", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      summary: adjustedSummary,
      foods: selectedFoods,
      details: adjustedResults
    })
  });

  const aiData = await aiRes.json();

  html += '<div class="card">';
  html += '<h3>AI 栄養分析</h3>';
  html += '<div>' + aiData.analysis.split("\\n").join("<br>") + '</div>';
  html += '</div>';

  document.getElementById("result").innerHTML = html;
}
</script>

</body>
</html>
"""
