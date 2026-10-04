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
from pathlib import Path
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
    
    # フィルタ条件:
    # 1. 「投稿祭」が含まれる
    # 2. 「シンプル車載動画投稿祭」が含まれない
    mask_fest = df["tags"].str.contains("投稿祭", na=False)
    mask_simple = df["tags"].str.contains("シンプル車載動画投稿祭", na=False)
    
    df = df[mask_fest & ~mask_simple].copy()
    
    df["startTime"] = pd.to_datetime(df["startTime"])
    df["year"] = df["startTime"].dt.year
    df["viewCounter"] = df["viewCounter"].astype(float)
    
    # グラフ設定
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

    years = [2021, 2022, 2023, 2024, 2025]
    colors = plt.get_cmap("viridis")(np.linspace(0, 0.8, len(years)))

    plt.figure(figsize=(12, 8))
    
    for i, year in enumerate(years):
        year_data = df[df["year"] == year]["viewCounter"]
        if len(year_data) > 0:
            # 再生数はレンジが広いため対数スケールで描画（x=0を除外するため +1）
            sns.kdeplot(np.log10(year_data + 1), label=f"{year}年", 
                        color=colors[i], linewidth=4, alpha=0.7)

    plt.xlabel("再生数 (log10)")
    plt.ylabel("密度 (Density)")
    plt.title("車載カテゴリ 投稿祭動画 再生数分布 (2021-2025)\n※「シンプル車載動画投稿祭」除外")
    plt.grid(True, linestyle="--", alpha=0.4)

    # 1000再生(10^3)の位置に縦線を引く
    plt.axvline(x=3, color='gray', linestyle='--', linewidth=2, alpha=0.6)
    plt.text(3.1, plt.ylim()[1]*0.9, "1000再生", color='gray', fontweight='bold')

    plt.legend(loc='upper right')
    
    # x軸のラベルを実際の再生数に変換して表示しやすくする
    xticks = [0, 1, 2, 3, 4, 5]
    xticklabels = ["1", "10", "100", "1k", "10k", "100k"]
    plt.xticks(xticks, xticklabels)
    plt.xlim(0, 5) # 10万再生までを表示対象とする
    
    plt.tight_layout()
    output_path = Path("results/onboard/fest_view_distribution_no_simple.png")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300)
    plt.close()
    
    print(f"Saved: {output_path}")

if __name__ == "__main__":
    main()
