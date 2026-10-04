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
    return df

def main():
    category = "explanation"
    target_user_id = 5482382
    
    df = preprocess(category)
    if df is None: return

    user_id_col = "userId" if "userId" in df.columns else "owner.id"

    # ユーザーの2025年の投稿を抽出
    df_user_2025 = df[(df[user_id_col] == target_user_id) & (df["year"] == 2025)]
    
    count = len(df_user_2025)
    
    print(f"### ユーザーID: {target_user_id} の2025年活動状況 (解説ジャンル)")
    if count > 0:
        print(f"活動状況: **あり**")
        print(f"2025年の投稿数: {count}本")
        
        # 長さの分布も軽く確認
        df_user_2025["lengthSeconds"] = df_user_2025["lengthSeconds"].astype(float)
        mean_len = df_user_2025["lengthSeconds"].mean() / 60.0
        print(f"平均再生時間: {mean_len:.2f}分")
    else:
        print(f"活動状況: なし")

if __name__ == "__main__":
    main()
