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
import matplotlib.pyplot as plt
import matplotlib_fontja
import pandas as pd
import seaborn as sns
import numpy as np
from pathlib import Path
from matplotlib.ticker import FuncFormatter
from common_utils import filter_software_talk

# グラフのスタイル設定
plt.rcParams['font.family'] = ['IBM Plex Sans JP', 'BIZ UDGothic', 'Yu Gothic', 'Meiryo', 'MS Gothic', 'sans-serif']
plt.rcParams['font.weight'] = 'bold'
plt.rcParams['font.size'] = 20
plt.rcParams['axes.titlesize'] = 32
plt.rcParams['axes.labelsize'] = 28
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['legend.fontsize'] = 20
plt.rcParams['xtick.labelsize'] = 20
plt.rcParams['ytick.labelsize'] = 20
plt.rcParams['figure.dpi'] = 200

GENRE_MAP = {
    "game": "実況",
    "theater": "劇場",
    "explanation": "解説",
    "kitchen": "キッチン",
    "onboard": "車載",
    "travel": "旅行",
    "software_talk": "ボイロ全体"
}
GENRE_ORDER = ["game", "explanation", "theater", "kitchen", "onboard", "travel", "software_talk"]
BINS = [50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000, 200000, 500000, 1000000]

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

    df = df[df["viewCounter"] > 0].copy()
    df["likeRatio"] = df["likeCounter"] / df["viewCounter"]
    
    return df

def plot_median_trends():
    output_dir = Path("results/like_ratio")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "median_trends_comparison.png"
    
    plt.figure(figsize=(14, 10))
    
    # ボイロ全体を除いたジャンルリスト
    target_genres = [g for g in GENRE_ORDER if g != "software_talk"]
    colors = sns.color_palette("Dark2", len(target_genres))
    
    for i, genre_id in enumerate(target_genres):
        df = load_genre_data(genre_id)
        if df is None:
            continue
            
        df['view_bin'] = pd.cut(df['viewCounter'], bins=BINS)
        grouped = df.groupby('view_bin', observed=False)
        median_like_ratio = grouped['likeRatio'].median()
        count_df = grouped['viewCounter'].count()
        
        valid_bins = count_df[count_df >= 10].index
        
        if not valid_bins.empty:
            plot_x = []
            plot_y = []
            for b in valid_bins:
                geom_mean = np.sqrt(b.left * b.right)
                plot_x.append(geom_mean)
                plot_y.append(median_like_ratio[b])
            
            label = GENRE_MAP[genre_id]
            plt.plot(plot_x, plot_y, color=colors[i], marker='o', linestyle='-', 
                     linewidth=2.5, markersize=8, label=label, zorder=10)

    plt.xscale("log")
    plt.xlim(50, 10**6)
    plt.ylim(0, 0.15) # データの広がりを強調するため上限を0.15に設定
    
    plt.xlabel("再生数")
    plt.ylabel("いいね率の中央値 (%)")
    plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x*100:g}'))
    
    plt.title("ジャンル別 いいね率中央値の推移 (2025年)")
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.legend(loc='lower center', ncol=3, frameon=True, facecolor='white', framealpha=0.9, fontsize=18)
    
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Generated median trends comparison: {output_path}")

def plot_median_trends_percentile():
    output_dir = Path("results/like_ratio")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "median_trends_comparison_percentile.png"
    
    plt.figure(figsize=(14, 10))
    
    # ボイロ全体を除いたジャンルリスト
    target_genres = [g for g in GENRE_ORDER if g != "software_talk"]
    colors = sns.color_palette("Dark2", len(target_genres))
    
    # 10%刻みのビン (0-10, 10-20, ..., 90-100)
    percentile_bins = np.linspace(0, 100, 11)
    
    for i, genre_id in enumerate(target_genres):
        df = load_genre_data(genre_id)
        if df is None:
            continue
            
        # 再生数の「上位％」を計算 (0=最高位, 100=最低位)
        df['top_percentile'] = (1 - df['viewCounter'].rank(pct=True)) * 100
        
        # 上位％でビン分け
        df['p_bin'] = pd.cut(df['top_percentile'], bins=percentile_bins, include_lowest=True)
        grouped = df.groupby('p_bin', observed=False)
        median_like_ratio = grouped['likeRatio'].median()
        count_df = grouped['viewCounter'].count()
        
        # 各ビンに十分なデータがある場合のみプロット
        valid_bins = count_df[count_df >= 10].index
        
        if not valid_bins.empty:
            plot_x = []
            plot_y = []
            for b in valid_bins:
                center = (b.left + b.right) / 2
                plot_x.append(center)
                plot_y.append(median_like_ratio[b])
            
            label = GENRE_MAP[genre_id]
            plt.plot(plot_x, plot_y, color=colors[i], marker='o', linestyle='-', 
                     linewidth=2.5, markersize=8, label=label, zorder=10)

    # 横軸を 100 -> 0 に設定
    plt.xlim(100, 0)
    plt.ylim(0, 0.15) # データの広がりを強調するため上限を0.15に設定
    
    plt.xlabel("ジャンル内の立ち位置（上位％）")
    plt.ylabel("いいね率の中央値 (%)")
    plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x*100:g}'))
    
    plt.title("ジャンル別 いいね率中央値の推移 (上位％基準, 2025年)")
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.legend(loc='lower center', ncol=3, frameon=True, facecolor='white', framealpha=0.9, fontsize=18)
    
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Generated median trends percentile comparison: {output_path}")

if __name__ == "__main__":
    plot_median_trends()
    plot_median_trends_percentile()
