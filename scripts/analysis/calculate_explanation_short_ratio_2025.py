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
    year_target = 2025
    min_len = 60 # 1分
    max_len = 120 # 2分
    
    df = preprocess(category)
    if df is None:
        print(f"Error: {category}.pickle not found.")
        return

    # userIdの列名
    user_id_col = "userId" if "userId" in df.columns else "owner.id"

    # 1. 2025年の全解説動画の投稿者数
    df_2025 = df[df["year"] == year_target]
    total_users_2025 = df_2025[user_id_col].nunique()
    total_videos_2025 = len(df_2025)

    # 2. 2025年の1-2分動画の投稿者数
    mask_short = (df_2025["lengthSeconds"] >= min_len) & (df_2025["lengthSeconds"] <= max_len)
    df_short = df_2025[mask_short]
    short_users_2025 = df_short[user_id_col].nunique()
    short_videos_2025 = len(df_short)

    print(f"### 2025年 解説ジャンルにおける1分-2分動画の割合")
    print(f"- 全投稿者数: {total_users_2025}人")
    print(f"- 1分-2分動画の投稿者数: {short_users_2025}人")
    print(f"- **投稿者数占有率: {(short_users_2025 / total_users_2025 * 100):.2f}%**")
    print("")
    print(f"- 全動画数: {total_videos_2025}本")
    print(f"- 1分-2分動画の数: {short_videos_2025}本")
    print(f"- **動画数占有率: {(short_videos_2025 / total_videos_2025 * 100):.2f}%**")

if __name__ == "__main__":
    main()
