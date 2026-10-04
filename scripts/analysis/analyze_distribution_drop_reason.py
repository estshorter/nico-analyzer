# /// script
# dependencies = [
#   "pandas",
#   "tabulate",
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
    min_len = 60
    max_len = 120

    results = []
    for year in [2024, 2025]:
        df_year = df[df["year"] == year]
        mask_short = (df_year["lengthSeconds"] >= min_len) & (df_year["lengthSeconds"] <= max_len)
        df_short = df_year[mask_short]
        
        total_short = len(df_short)
        user_14523983 = len(df_short[df_short[user_id_col] == 14523983])
        user_5482382 = len(df_short[df_short[user_id_col] == 5482382])
        
        results.append({
            "Year": year,
            "Total 1-2m": total_short,
            "User 14523983 (1-2m)": user_14523983,
            "User 5482382 (1-2m)": user_5482382,
            "Others (1-2m)": total_short - user_14523983 - user_5482382
        })

    res_df = pd.DataFrame(results)
    print(res_df.to_markdown(index=False))

    # また、14523983の2025年の全投稿数も確認
    user_14523983_2025_all = len(df[(df["year"] == 2025) & (df[user_id_col] == 14523983)])
    print(f"\nUser 14523983 total posts in 2025: {user_14523983_2025_all}")

if __name__ == "__main__":
    main()
