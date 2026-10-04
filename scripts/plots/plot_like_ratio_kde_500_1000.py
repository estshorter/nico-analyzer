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
import matplotlib.pyplot as plt
import matplotlib_fontja
import pandas as pd
import seaborn as sns
import numpy as np
from pathlib import Path
from matplotlib.ticker import FuncFormatter
from common_utils import filter_software_talk

# グラフのスタイル設定 (既存の分布グラフに合わせる)
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

GENRE_MAP = {
    "game": "ゲーム",
    "theater": "劇場",
    "explanation": "解説",
    "kitchen": "キッチン",
    "onboard": "車載",
    "travel": "旅行",
    "software_talk": "ボイロ全体"
}
GENRE_ORDER = ["game", "theater", "explanation", "kitchen", "onboard", "travel", "software_talk"]

def load_genre_data(genre_id):
    input_path = Path(f"results/{genre_id}.pickle")
    if not input_path.exists():
        return None

    with open(input_path, "rb") as f:
        raw_data = pickle.load(f)
    
    data = raw_data["data"] if isinstance(raw_data, dict) else raw_data
    df = pd.DataFrame(data)
    
    if genre_id == "software_talk":
        df = filter_software_talk(df)

    df["startTime"] = pd.to_datetime(df["startTime"])
    df = df[df["startTime"].dt.year == 2025].copy()
    
    if df.empty:
        return None

    # 500〜1000再生の区間に絞る
    df = df[(df["viewCounter"] >= 500) & (df["viewCounter"] < 1000)].copy()
    
    if df.empty:
        return None
        
    df["likeRatio"] = df["likeCounter"] / df["viewCounter"]
    
    return df

def main():
    output_dir = Path("results/like_ratio")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "like_ratio_kde_500_1000.png"
    
    plt.figure(figsize=(12, 8))
    
    # Dark2パレットの色を取得
    colors = plt.get_cmap("Dark2").colors
    
    for i, genre_id in enumerate(GENRE_ORDER):
        df = load_genre_data(genre_id)
        if df is None or df.empty:
            continue
            
        label = GENRE_MAP[genre_id]
        
        # ボイロ全体を目立たせる（黒の太い破線）
        if genre_id == "software_talk":
            sns.kdeplot(df["likeRatio"], label=label, 
                        color="black", linestyle="--", linewidth=4, alpha=0.8)
        else:
            sns.kdeplot(df["likeRatio"], label=label, 
                        color=colors[i % 8], linewidth=4, alpha=0.8)

    # X軸の設定（いいね率 %）
    plt.gca().xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x*100:g}'))
    plt.xlim(0, 0.4) # 0%〜40%
    
    plt.xlabel("いいね率 (%)")
    plt.ylabel("密度 (Density)")
    plt.title("500-1000再生層 ジャンル別いいね率分布 (KDE)")
    plt.grid(True, which="both", linestyle="--", alpha=0.4)
    plt.legend(loc='upper right', frameon=True, shadow=False)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Generated KDE plot: {output_path}")

if __name__ == "__main__":
    main()
