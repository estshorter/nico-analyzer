# /// script
# dependencies = [
#   "pandas",
# ]
# ///

import pickle
from pathlib import Path
import pandas as pd

def preprocess(category):
    pickle_path = Path(f"results/{category}.pickle")
    if not pickle_path.exists():
        return None
    with open(pickle_path, "rb") as f:
        recv = pickle.load(f)
    df = pd.json_normalize(recv["data"])
    df["startTime"] = pd.to_datetime(df["startTime"])
    df["year"] = df["startTime"].dt.year
    df["lengthSeconds"] = df["lengthSeconds"].astype(float)
    return df

def main():
    category = "explanation"
    df = preprocess(category)
    if df is None: return
    user_id_col = "userId" if "userId" in df.columns else "owner.id"

    yearly_heavy_users = {}
    for year in [2023, 2024, 2025]:
        df_year = df[df["year"] == year]
        mask = (df_year["lengthSeconds"] >= 0) & (df_year["lengthSeconds"] <= 120)
        df_short = df_year[mask]
        counts = df_short[user_id_col].value_counts()
        heavy = counts[counts >= 100].index.tolist()
        yearly_heavy_users[year] = set(map(int, heavy))

    u2023 = yearly_heavy_users[2023]
    u2024 = yearly_heavy_users[2024]
    u2025 = yearly_heavy_users[2025]

    print("### 100本以上投稿者の年次比較 (0-2分)")
    
    print(f"\n#### 2023年 vs 2024年")
    print(f"- 共通の常連: {u2023 & u2024}")
    print(f"- 2023のみ (2024年に100本未満へ): {u2023 - u2024}")
    print(f"- 2024からの新勢力: {u2024 - u2023}")

    print(f"\n#### 2024年 vs 2025年")
    print(f"- 継続中の常連: {u2024 & u2025}")
    print(f"- 2024年を最後に脱落 (100本未満へ): {u2024 - u2025}")
    print(f"- 2025年からの新勢力: {u2025 - u2024}")

    # 脱落者の2025年の活動も念のため確認
    dropout_2024 = u2024 - u2025
    print(f"\n#### 2024年の脱落者の2025年活動状況 (全尺)")
    for uid in dropout_2024:
        count_2025 = len(df[(df["year"] == 2025) & (df[user_id_col] == uid)])
        print(f"- ユーザー {uid}: 2025年投稿数 {count_2025}本")

if __name__ == "__main__":
    main()
