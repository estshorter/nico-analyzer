# /// script
# dependencies = [
#   "pandas",
#   "numpy",
# ]
# ///

import pickle
import pandas as pd
import numpy as np
from pathlib import Path

def check_distribution(category, year=2025):
    pickle_path = Path(f"results/{category}.pickle")
    if not pickle_path.exists():
        return
        
    with open(pickle_path, "rb") as f:
        recv = pickle.load(f)
    df = pd.json_normalize(recv["data"])
    df["startTime"] = pd.to_datetime(df["startTime"])
    df["year"] = df["startTime"].dt.year
    df["viewCounter"] = df["viewCounter"].astype(float)
    
    data = df[df["year"] == year]["viewCounter"]
    if len(data) == 0:
        return

    print(f"--- {category} ({year}) ---")
    print(f"Total Videos: {len(data)}")
    print(f"Min: {data.min()}")
    print(f"10th percentile: {np.percentile(data, 10)}")
    print(f"25th percentile: {np.percentile(data, 25)}")
    print(f"50th percentile (Median): {np.percentile(data, 50)}")
    print(f"75th percentile: {np.percentile(data, 75)}")
    print(f"90th percentile: {np.percentile(data, 90)}")
    print(f"99th percentile: {np.percentile(data, 99)}")
    print(f"Max: {data.max()}")
    print(f"Mean: {data.mean():.1f}")

if __name__ == "__main__":
    # 主要な3ジャンルで分布を確認
    for cat in ["onboard", "kitchen", "game", "software_talk"]:
        check_distribution(cat)
