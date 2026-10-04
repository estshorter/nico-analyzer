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
    target_user_id = 5482382
    df = preprocess(category)
    if df is None: return

    user_id_col = "userId" if "userId" in df.columns else "owner.id"
    df_user = df[df[user_id_col] == target_user_id]

    stats = []
    for year in [2024, 2025]:
        df_year = df_user[df_user["year"] == year]
        if df_year.empty: continue
        
        lens = df_year["lengthSeconds"]
        
        # 区分け
        count_under_1m = len(lens[lens < 60])
        count_1to2m = len(lens[(lens >= 60) & (lens <= 120)])
        count_over_2m = len(lens[lens > 120])
        
        stats.append({
            "Year": year,
            "Total Videos": len(lens),
            "Mean (sec)": f"{lens.mean():.1f}",
            "Median (sec)": f"{lens.median():.1f}",
            "< 1m (count)": count_under_1m,
            "1-2m (count)": count_1to2m,
            "> 2m (count)": count_over_2m,
            "1-2m (%)": f"{(count_1to2m/len(lens)*100):.1f}%"
        })

    print(f"### ユーザーID: {target_user_id} の投稿時間詳細分析")
    print(pd.DataFrame(stats).to_markdown(index=False))

if __name__ == "__main__":
    main()
