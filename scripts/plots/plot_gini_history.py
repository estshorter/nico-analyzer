# /// script
# dependencies = [
#   "matplotlib",
#   "matplotlib-fontja",
#   "pandas",
#   "seaborn",
#   "numpy",
#   "tabulate",
# ]
# ///

import pickle
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

def calculate_gini(values):
    """ジニ係数を計算する"""
    if len(values) == 0:
        return 0
    sorted_values = np.sort(values)
    n = len(values)
    index = np.arange(1, n + 1)
    # G = (2 * sum(i * x_i) / (n * sum(x_i))) - (n + 1) / n
    return (2 * np.sum(index * sorted_values) / (n * np.sum(sorted_values))) - (n + 1) / n

def main():
    # フォント設定
    plt.rcParams['font.family'] = ['IBM Plex Sans JP', 'BIZ UDGothic', 'Yu Gothic', 'Meiryo', 'MS Gothic', 'sans-serif']
    plt.rcParams['font.weight'] = 'bold'
    plt.rcParams['font.size'] = 16
    plt.rcParams['axes.titlesize'] = 24
    plt.rcParams['axes.labelsize'] = 20
    plt.rcParams['axes.labelweight'] = 'bold'
    plt.rcParams['axes.titleweight'] = 'bold'
    plt.rcParams['legend.fontsize'] = 14
    plt.rcParams['xtick.labelsize'] = 16
    plt.rcParams['ytick.labelsize'] = 16
    plt.rcParams['figure.dpi'] = 200

    with open("config.toml", "rb") as f:
        cfg = tomllib.load(f)
    
    target_years = range(2020, 2026)

    # 指定された順序とラベル
    category_map = {
        "game": "実況",
        "software_talk": "全体",
        "explanation": "解説",
        "theater": "劇場",
        "travel": "旅行",
        "kitchen": "キッチン",
        "onboard": "車載"
    }
    target_categories = list(category_map.keys())

    plt.figure(figsize=(12, 8))
    colors = plt.get_cmap("Dark2").colors

    for i, category in enumerate(target_categories):
        if category not in cfg: continue

        df = preprocess(category)
        if df is None: continue

        gini_history = []
        years_present = []

        for year in target_years:
            year_data = df[df["year"] == year]["viewCounter"]
            if len(year_data) < 10: continue

            gini = calculate_gini(year_data.values)
            gini_history.append(gini)
            years_present.append(year)

        label = category_map[category]
        plt.plot(years_present, gini_history, marker='o', label=label, color=colors[i % 8], linewidth=4, markersize=10)

    plt.xlabel("年")
    plt.ylabel("ジニ係数 (格差の指標)")
    plt.title("ジャンル別ジニ係数の推移 (2020-2025)")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # 2017年からの表示を確実にする
    plt.xticks(target_years)
    
    plt.tight_layout()
    output_path = Path("results/gini_coefficient_history.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Saved Gini coefficient history plot to {output_path}")

if __name__ == "__main__":
    main()
