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

    for year in [2023, 2024, 2025]:
        df_year = df[df["year"] == year]
        mask = (df_year["lengthSeconds"] >= 0) & (df_year["lengthSeconds"] <= 120)
        df_short = df_year[mask]
        counts = df_short[user_id_col].value_counts()
        heavy = counts[counts >= 100]
        print(f"Year {year}: {len(heavy)} users with 100+ videos")

if __name__ == "__main__":
    main()
