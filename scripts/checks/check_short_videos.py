# /// script
# dependencies = [
#   "pandas",
#   "numpy",
#   "tabulate",
# ]
# ///

import pickle
import tomllib
from pathlib import Path
import pandas as pd
import numpy as np

from common_utils import filter_software_talk

def preprocess(category):
    pickle_path = Path(f"results/{category}.pickle")
    if not pickle_path.exists(): return None
    with open(pickle_path, "rb") as f:
        recv = pickle.load(f)
    df = pd.json_normalize(recv["data"])
    df["startTime"] = pd.to_datetime(df["startTime"])
    df["year"] = df["startTime"].dt.year
    df["viewCounter"] = df["viewCounter"].astype(float)
    if "lengthSeconds" in df.columns:
        df["lengthSeconds"] = pd.to_numeric(df["lengthSeconds"], errors='coerce')
        df = df.dropna(subset=["lengthSeconds"])
    else: return None
    return df

def main():
    target_years = [2018, 2021, 2025]
    all_results = []

    # 特に怪しい「劇場」と、比較用の「全体（ソフトウェアトーク）」で調査
    for category in ["theater", "software_talk"]:
        df = preprocess(category)
        if df is None: continue
        
        for year in target_years:
            year_data = df[df["year"] == year]
            if len(year_data) == 0: continue
            
            total_count = len(year_data)
            # 30秒以下の動画
            short_videos = year_data[year_data["lengthSeconds"] <= 30]
            short_count = len(short_videos)
            short_ratio = (short_count / total_count) * 100
            
            # 30秒以下の動画の再生数中央値
            short_median_views = np.median(short_videos["viewCounter"]) if short_count > 0 else 0
            # 30秒超の動画の再生数中央値
            long_median_views = np.median(year_data[year_data["lengthSeconds"] > 30]["viewCounter"])
            
            all_results.append({
                "Genre": "劇場" if category == "theater" else "全体",
                "Year": year,
                "Total": total_count,
                "≤30s Count": short_count,
                "≤30s Ratio": f"{short_ratio:.1f}%",
                "≤30s Median Views": int(short_median_views),
                ">30s Median Views": int(long_median_views)
            })

    result_df = pd.DataFrame(all_results)
    print(result_df.to_markdown(index=False))

if __name__ == "__main__":
    main()
