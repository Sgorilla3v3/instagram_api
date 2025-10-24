import json
import pandas as pd
import os

# =====================================
# 1️⃣ 파일 경로 설정
# =====================================
input_path = r"C:\Users\Administrator\Desktop\git_pre\instagram_api\scripts\all_user_media_with_insights.json"  # JSON 파일 경로 수정
output_path = r"C:\Users\Administrator\Desktop\git_pre\instagram_api\scripts\all_user_media_with_insights.csv"  # 저장할 CSV 경로

# =====================================
# 2️⃣ JSON 파일 불러오기
# =====================================
with open(input_path, "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"📦 불러온 게시물 개수: {len(data)}")

# =====================================
# 3️⃣ JSON → 평탄화 (Flatten)
# =====================================
rows = []

for post in data:
    post_id = post.get("id", "")
    row = {"id": post_id}

    insights = post.get("insights", [])
    for insight in insights:
        name = insight.get("name")
        # 값이 존재하는지 확인
        if insight.get("values") and isinstance(insight["values"], list):
            value = insight["values"][0].get("value", 0)
        else:
            value = 0
        row[name] = value

    rows.append(row)

# =====================================
# 4️⃣ DataFrame 변환
# =====================================
df = pd.DataFrame(rows)

# 결측치는 0으로 처리
df.fillna(0, inplace=True)

# =====================================
# 5️⃣ engagement_rate(참여율) 추가 (선택)
# =====================================
if "reach" in df.columns and "total_interactions" in df.columns:
    df["engagement_rate(%)"] = df.apply(
        lambda x: round((x["total_interactions"] / x["reach"] * 100), 2)
        if x["reach"] != 0 else 0,
        axis=1
    )

# =====================================
# 6️⃣ CSV로 저장
# =====================================
df.to_csv(output_path, index=False, encoding="utf-8-sig")

print(f"✅ CSV 저장 완료: {output_path}")
print("📊 미리보기:")
print(df.head())
