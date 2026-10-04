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
    if not pickle_path.exists():
        return None
        
    with open(pickle_path, "rb") as f:
        recv = pickle.load(f)
    df = pd.json_normalize(recv["data"])

    if category == "software_talk":
        df = filter_software_talk(df)

    df["startTime"] = pd.to_datetime(df["startTime"])
    df["year"] = df["startTime"].dt.year
    df["viewCounter"] = df["viewCounter"].astype(float)
    return df

def main():
    with open("config.toml", "rb") as f:
        cfg = tomllib.load(f)
    
    target_years = [2018, 2021, 2025]
    all_results = []

    for category in cfg.keys():
        df = preprocess(category)
        if df is None: continue
            
        genre_name = cfg[category]["title"].replace("ニコニコ ", "").replace(" 年次統計", "")
        
        for year in target_years:
            year_data = df[df["year"] == year]["viewCounter"]
            if len(year_data) == 0:
                continue
            
            all_results.append({
                "Genre": genre_name,
                "Year": year,
                "Mean": int(np.mean(year_data)),
                "Median": int(np.median(year_data))
            })

    result_df = pd.DataFrame(all_results)
    
    # ピボットして表を作成
    pivot_mean = result_df.pivot(index="Genre", columns="Year", values="Mean")
    pivot_median = result_df.pivot(index="Genre", columns="Year", values="Median")
    
    md = "### ジャンル別 再生数平均値（Mean）推移\n\n"
    md += pivot_mean.to_markdown() + "\n\n"
    md += "### ジャンル別 再生数中央値（Median）推移\n\n"
    md += pivot_median.to_markdown() + "\n\n"
    
    print(md)
    
    # 比較用に2025年分を抜粋して分析用テキスト作成
    df_2025 = result_df[result_df["Year"] == 2025].copy()
    df_2025["Ratio (Mean/Median)"] = df_2025["Mean"] / df_2025["Median"]
    print("### 2025年 平均/中央値 比率（格差の指標）")
    print(df_2025[["Genre", "Mean", "Median", "Ratio (Mean/Median)"]].sort_values("Ratio (Mean/Median)", ascending=False).to_markdown(index=False))

if __name__ == "__main__":
    main()
