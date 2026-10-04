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
    year_target = 2024
    min_len = 0
    max_len = 120
    
    df = preprocess(category)
    if df is None: return

    user_id_col = "userId" if "userId" in df.columns else "owner.id"

    df_2024 = df[df["year"] == year_target]
    mask_short = (df_2024["lengthSeconds"] >= min_len) & (df_2024["lengthSeconds"] <= max_len)
    df_short = df_2024[mask_short]
    
    user_counts = df_short[user_id_col].value_counts().reset_index()
    user_counts.columns = ["userId", "videoCount"]
    
    heavy_users = user_counts[user_counts["videoCount"] >= 100]
    
    print(f"### 2024年 解説ジャンル (0分-2分) 100本以上投稿者一覧")
    print(f"該当者数: {len(heavy_users)}人\n")
    print(f"| 順位 | ユーザーID | 投稿数 |")
    print(f"| :--- | :--- | :--- |")
    for i, row in heavy_users.iterrows():
        print(f"| {i+1} | {int(row['userId'])} | {int(row['videoCount'])}本 |")

if __name__ == "__main__":
    main()
