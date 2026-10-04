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
    target_years = [2023, 2024, 2025]
    min_len = 60 # 1分
    max_len = 120 # 2分
    
    df = preprocess(category)
    if df is None:
        print(f"Error: {category}.pickle not found.")
        return

    # userIdの列名を探す
    user_id_col = "userId" if "userId" in df.columns else "owner.id"

    print(f"### 解説ジャンル 1分-2分動画の推移")
    print(f"| 年 | 投稿数 | 投稿者数 |")
    print(f"| :--- | :--- | :--- |")
    
    for year in target_years:
        mask = (df["year"] == year) & (df["lengthSeconds"] >= min_len) & (df["lengthSeconds"] <= max_len)
        filtered_df = df[mask]
        video_count = len(filtered_df)
        user_count = filtered_df[user_id_col].nunique() if user_id_col in df.columns else 0
        print(f"| {year}年 | {video_count} | {user_count} |")




if __name__ == "__main__":
    main()
