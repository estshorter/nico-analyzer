# /// script
# dependencies = [
#   "matplotlib",
#   "matplotlib-fontja",
#   "pandas",
#   "seaborn",
#   "numpy",
#   "scipy",
# ]
# ///

import pickle
import tomllib
from pathlib import Path

import matplotlib_fontja
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
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
    # ターゲットカテゴリーのフィルタリング
    target_categories = ["onboard", "travel", "game", "theater", "kitchen", "explanation"]
    year_target = 2025
    highlight_target = "onboard"
    
    # フォント設定
    plt.rcParams['font.family'] = ['IBM Plex Sans JP', 'BIZ UDGothic', 'Yu Gothic', 'Meiryo', 'MS Gothic', 'sans-serif']
    plt.rcParams['font.weight'] = 'bold'
    plt.rcParams['font.size'] = 16
    plt.rcParams['axes.titlesize'] = 24
    plt.rcParams['axes.labelsize'] = 20
    plt.rcParams['axes.labelweight'] = 'bold'
    plt.rcParams['axes.titleweight'] = 'bold'
    plt.rcParams['legend.fontsize'] = 16
    plt.rcParams['xtick.labelsize'] = 16
    plt.rcParams['ytick.labelsize'] = 16
    plt.rcParams['figure.dpi'] = 200

    log_formatter = ticker.FuncFormatter(lambda x, pos: f'{int(x):,}' if x >= 1 else f'{x}')
    colors = plt.get_cmap("Dark2").colors

    plt.figure(figsize=(12, 8))
    
    label_map = {
        "onboard": "車載",
        "travel": "旅行",
        "game": "実況",
        "theater": "劇場",
        "kitchen": "キッチン",
        "explanation": "解説"
    }

    for i, category in enumerate(target_categories):
        df = preprocess(category)
        if df is None: continue
        year_data = df[df["year"] == year_target]["viewCounter"]
        year_data = year_data[year_data > 0]
        
        if category == highlight_target:
            color = colors[i % 8]
            linewidth = 6
            alpha = 1.0
            zorder = 10
        else:
            color = "#d1d5db" # Gray
            linewidth = 2
            alpha = 0.5
            zorder = 1
            
        sns.kdeplot(year_data, log_scale=True, label=label_map[category], 
                    color=color, linewidth=linewidth, alpha=alpha, zorder=zorder)

    plt.gca().xaxis.set_major_formatter(log_formatter)
    plt.xlabel("再生数 (対数軸)")
    plt.ylabel("密度 (Density)")
    plt.title(f"{year_target}年 主要ジャンル別再生数分布 ({label_map[highlight_target]}ハイライト)")
    plt.grid(True, which="both", linestyle="--", alpha=0.4)
    plt.legend(loc='upper right', frameon=True, shadow=False)
    
    plt.xlim(10, 100000)
    
    plt.tight_layout()
    output_path = f"results/all_genres_view_distribution_2025_highlight_{highlight_target}.png"
    plt.savefig(output_path, dpi=300)
    plt.close()
    
    print(f"Saved highlighted distribution plot to {output_path}")

if __name__ == "__main__":
    main()
