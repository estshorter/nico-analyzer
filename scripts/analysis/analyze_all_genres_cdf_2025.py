# /// script
# dependencies = [
#   "matplotlib",
#   "matplotlib-fontja",
#   "pandas",
#   "seaborn",
#   "numpy",
# ]
# ///

import pickle
import sys
import tomllib
from pathlib import Path

import matplotlib_fontja
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns

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
    
    plt.figure(figsize=(12, 8))
    # software_talk（全体）を除外するか、最後に描画して比較しやすくする
    categories = list(cfg.keys())
    # 全体データは最後に描画するために調整
    if "software_talk" in categories:
        categories.remove("software_talk")
        categories.append("software_talk")

    colors = sns.color_palette("husl", len(categories))
    
    year_target = 2025
    has_plot = False

    for i, category in enumerate(categories):
        df = preprocess(category)
        if df is None:
            continue
            
        year_data = df[df["year"] == year_target]["viewCounter"]
        if len(year_data) == 0:
            continue
            
        sorted_views = np.sort(year_data.values)
        cdf = np.arange(1, len(sorted_views) + 1) / len(sorted_views)
        
        label = cfg[category]["title"].replace("ニコニコ ", "").replace(" 年次統計", "")
        linewidth = 3 if category == "software_talk" else 2
        linestyle = "--" if category == "software_talk" else "-"
        alpha = 0.8 if category != "software_talk" else 1.0
        
        plt.plot(np.maximum(sorted_views, 1), cdf * 100, label=label, color=colors[i], 
                 linewidth=linewidth, linestyle=linestyle, alpha=alpha)
        has_plot = True

    if not has_plot:
        print("No data found for 2025.")
        return

    plt.xscale("log")
    plt.xlabel("再生数 (対数軸)")
    plt.ylabel("累積割合 (%)")
    plt.title(f"{year_target}年 ジャンル別再生数累積分布 (CDF) 比較")
    plt.grid(True, which="both", linestyle="--", alpha=0.5)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # 補助線
    for h in [25, 50, 75]:
        plt.axhline(h, color='gray', linestyle=':', alpha=0.3)

    plt.tight_layout()
    
    output_path = Path("results/all_genres_view_cdf_2025.png")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Saved: {output_path}")
    plt.close()

if __name__ == "__main__":
    main()
