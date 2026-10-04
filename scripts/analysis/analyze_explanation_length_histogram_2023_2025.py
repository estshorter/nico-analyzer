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
from pathlib import Path

import matplotlib_fontja
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np

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
    label = "解説"
    target_years = [2023, 2024, 2025]
    
    plt.rcParams['font.family'] = ['IBM Plex Sans JP', 'BIZ UDGothic', 'Yu Gothic', 'Meiryo', 'MS Gothic', 'sans-serif']
    plt.rcParams['font.weight'] = 'bold'
    plt.rcParams['font.size'] = 16
    plt.rcParams['axes.titlesize'] = 24
    plt.rcParams['axes.labelsize'] = 20
    plt.rcParams['figure.dpi'] = 200

    plt.figure(figsize=(14, 8))
    
    df = preprocess(category)
    if df is None:
        print(f"Error: {category}.pickle not found.")
        return

    # 1分単位のビンを設定 (0分から10分まで)
    bins = np.arange(0, 12, 1)

    colors = sns.color_palette("husl", len(target_years))

    for i, year in enumerate(target_years):
        year_data = df[df["year"] == year]["lengthSeconds"]
        if year_data.empty: continue
            
        year_data_min = year_data / 60.0 # 分に変換
        
        # ヒストグラム (密度ではなく、単純な本数の比較が見やすいように element="step" を使用)
        sns.histplot(year_data_min, bins=bins, label=f"{year}年", 
                     color=colors[i], element="step", fill=True, alpha=0.2, linewidth=3)

    plt.xlabel("再生時間 (分)")
    plt.ylabel("動画数")
    plt.title(f"{label}ジャンル 再生時間ヒストグラム (2023-2025)")
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.legend(loc='upper right')
    
    plt.xlim(0, 10)
    plt.xticks(range(0, 11, 1))
    
    plt.tight_layout()
    output_path = f"results/{category}/{category}_length_histogram_2023_2025.png"
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Saved: {output_path}")

if __name__ == "__main__":
    main()
