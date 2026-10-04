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
import matplotlib.ticker as ticker
import pandas as pd
import numpy as np
import seaborn as sns

def main():
    category = "onboard"
    pickle_path = Path(f"results/{category}.pickle")
    if not pickle_path.exists():
        print(f"File not found: {pickle_path}")
        return
        
    with open(pickle_path, "rb") as f:
        recv = pickle.load(f)
    df = pd.json_normalize(recv["data"])
    
    # 「投稿祭」を除外
    df = df[~df["tags"].str.contains("祭", na=False)]
    
    df["startTime"] = pd.to_datetime(df["startTime"])
    df["year"] = df["startTime"].dt.year
    df["lengthSeconds"] = df["lengthSeconds"].astype(float)

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
    
    for i, year in enumerate(years):
        year_data = df[df["year"] == year]["lengthSeconds"]
        year_data = year_data / 60.0 # 分に変換
        
        sns.kdeplot(year_data, label=f"{year}年", 
                    color=colors[i], linewidth=4, alpha=0.7)

    plt.xlabel("再生時間 (分)")
    plt.ylabel("密度 (Density)")
    plt.title("ニコニコ車載動画 再生時間分布の推移 (投稿祭除く)")
    plt.grid(True, linestyle="--", alpha=0.4)

    # 3分の位置に縦線を引く
    plt.axvline(x=3, color='gray', linestyle='--', linewidth=2, alpha=0.6)

    plt.legend(loc='upper right')
    
    plt.xlim(0, 30)
    plt.xticks(range(0, 31, 5))
    
    plt.tight_layout()
    output_path = Path("results/onboard/length_distribution_history_combined_linear_30m_no_simple.png")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Saved: {output_path}")

if __name__ == "__main__":
    main()
