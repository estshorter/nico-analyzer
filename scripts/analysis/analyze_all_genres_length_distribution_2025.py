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
    df["lengthSeconds"] = df["lengthSeconds"].astype(float)
    return df

def main():
    with open("config.toml", "rb") as f:
        cfg = tomllib.load(f)
    
    target_categories = ["onboard", "travel", "game", "theater", "kitchen", "explanation"]
    year_target = 2025
    
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

    # 秒を分に変換して表示するフォーマッター
    def time_formatter(x, pos):
        if x < 60:
            return f'{int(x)}s'
        else:
            return f'{int(x/60)}m'

    log_formatter = ticker.FuncFormatter(time_formatter)
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
        year_data = df[df["year"] == year_target]["lengthSeconds"]
        year_data = year_data[year_data > 0]
        
        sns.kdeplot(year_data, log_scale=True, label=label_map[category], 
                    color=colors[i % 8], linewidth=4, alpha=0.8)

    plt.gca().xaxis.set_major_formatter(log_formatter)
    # 主要な時間の目盛りを設定
    plt.gca().xaxis.set_major_locator(ticker.LogLocator(base=10, subs=[1.0, 2.0, 3.0, 5.0]))
    
    plt.xlabel("再生時間")
    plt.ylabel("密度 (Density)")
    plt.title(f"{year_target}年 主要ジャンル別再生時間分布 (KDE)")
    plt.grid(True, which="both", linestyle="--", alpha=0.4)
    plt.legend(loc='upper right', frameon=True, shadow=False)
    
    plt.xlim(10, 7200) # 10秒から2時間
    
    plt.tight_layout()
    output_path = "results/all_genres_length_distribution_2025.png"
    plt.savefig(output_path, dpi=300)
    plt.close()
    
    print(f"Saved length distribution plot to {output_path}")

if __name__ == "__main__":
    main()
