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
    
    # 共通フィルタリング: 「シンプル車載動画投稿祭」および「ずんだもん」を除外
    df = df[~df["tags"].str.contains("シンプル車載動画投稿祭", na=False)]
    df = df[~df["tags"].str.contains("ずんだもん", na=False)]
    df["startTime"] = pd.to_datetime(df["startTime"])
    df["lengthSeconds"] = df["lengthSeconds"].astype(float)
    df["lengthMinutes"] = df["lengthSeconds"] / 60.0

    df_2023 = df[df["startTime"].dt.year == 2023]
    df_2022 = df[df["startTime"].dt.year == 2022]

    # 期間分け
    data_groups = {
        "2022年 通年": df_2022["lengthMinutes"],
        "2023年 通年": df_2023["lengthMinutes"],
        "2023年 1-6月": df_2023[df_2023["startTime"].dt.month <= 6]["lengthMinutes"],
        "2023年 7-12月": df_2023[df_2023["startTime"].dt.month > 6]["lengthMinutes"]
    }

    plt.rcParams['font.family'] = ['IBM Plex Sans JP', 'BIZ UDGothic', 'Yu Gothic', 'Meiryo', 'MS Gothic', 'sans-serif']
    plt.rcParams['font.weight'] = 'bold'
    plt.rcParams['font.size'] = 16
    plt.rcParams['figure.dpi'] = 200

    plt.figure(figsize=(12, 8))
    
    colors = ["#440154", "#414487", "#2a788e", "#22a884"] # Viridis sequence
    
    for i, (label, data) in enumerate(data_groups.items()):
        sns.kdeplot(data, label=label, color=colors[i], linewidth=4, alpha=0.7)

    plt.xlabel("再生時間 (分)")
    plt.ylabel("密度 (Density)")
    plt.title("ニコニコ車載動画 再生時間分布 2022 vs 2023 (0-30分)\n※「シンプル車載動画投稿祭」「ずんだもん」除外")
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.legend(loc='upper right')
    
    plt.xlim(0, 30)
    plt.xticks(range(0, 31, 5))
    
    plt.tight_layout()
    output_path = Path("results/onboard/length_distribution_2023_split_no_simple.png")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Saved: {output_path}")

if __name__ == "__main__":
    main()
