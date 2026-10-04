# /// script
# dependencies = [
#   "matplotlib",
#   "matplotlib-fontja",
#   "pandas",
#   "numpy",
# ]
# ///

import pickle
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def main():
    category = "onboard"
    pickle_path = Path(f"results/{category}.pickle")
    if not pickle_path.exists():
        print(f"File not found: {pickle_path}")
        return
        
    with open(pickle_path, "rb") as f:
        recv = pickle.load(f)
    df = pd.json_normalize(recv["data"])
    
    # 「シンプル車載動画投稿祭」を除外
    df = df[~df["tags"].str.contains("シンプル車載動画投稿祭", na=False)]
    
    df["startTime"] = pd.to_datetime(df["startTime"])
    df["year"] = df["startTime"].dt.year
    df["lengthSeconds"] = df["lengthSeconds"].astype(float)
    df["lengthMinutes"] = df["lengthSeconds"] / 60.0

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

    years = [2022, 2023, 2024, 2025]
    colors = plt.get_cmap("viridis")(np.linspace(0, 0.8, len(years)))

    plt.figure(figsize=(12, 8))
    
    # 0分から30分まで、1分刻みのビン
    bins = np.arange(0, 31, 1)
    bin_centers = bins[:-1] + 0.5

    for i, year in enumerate(years):
        year_data = df[df["year"] == year]["lengthMinutes"]
        
        # ヒストグラムの計算
        counts, _ = np.histogram(year_data, bins=bins)
        
        plt.plot(bin_centers, counts, label=f"{year}年", 
                 color=colors[i], linewidth=3, marker='o', markersize=4, alpha=0.8)

    plt.xlabel("再生時間 (分)")
    plt.ylabel("投稿数")
    plt.title("ニコニコ車載動画 再生時間別投稿数推移 (2022-2025)\n※「シンプル車載動画投稿祭」除外")
    plt.grid(True, linestyle="--", alpha=0.4)

    # 3分の位置に縦線を引く
    plt.axvline(x=3, color='gray', linestyle='--', linewidth=2, alpha=0.6)

    plt.legend(loc='upper right')
    
    plt.xlim(0, 30)
    plt.xticks(range(0, 31, 5))
    
    plt.tight_layout()
    output_path = Path("results/onboard/length_distribution_line_history_5y.png")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Saved: {output_path}")

if __name__ == "__main__":
    main()
