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
    df = preprocess(category)
    user_id_col = "userId" if "userId" in df.columns else "owner.id"
    df_2025 = df[df["year"] == year_target]
    
    # Check different length ranges
    ranges = [(0, 60), (60, 120), (120, 180)]
    for r in ranges:
        mask = (df_2025["lengthSeconds"] >= r[0]) & (df_2025["lengthSeconds"] <= r[1])
        df_range = df_2025[mask]
        counts = df_range[user_id_col].value_counts()
        total = len(df_range)
        if total > 0:
            top2_sum = counts.head(2).sum()
            print(f"Range {r[0]}-{r[1]}s: Total={total}, Top2={top2_sum} ({(top2_sum/total*100):.1f}%)")

if __name__ == "__main__":
    main()
