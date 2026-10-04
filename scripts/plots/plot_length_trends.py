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

def load_genre_data_raw(genre_id):
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
    df["year"] = df["startTime"].dt.year
    df["lengthMinutes"] = df["lengthSeconds"] / 60.0
    
    return df

def plot_length_trends_comparison_percentile(year=2025):
    output_dir = Path("results/length")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"length_trends_comparison_percentile_{year}.png"
    
    plt.figure(figsize=(14, 10))
    
    target_genres = [g for g in GENRE_ORDER if g != "software_talk"]
    colors = sns.color_palette("Dark2", len(target_genres))
    
    percentile_bins = np.linspace(0, 100, 11)
    
    for i, genre_id in enumerate(target_genres):
        df_full = load_genre_data_raw(genre_id)
        if df_full is None:
            continue
            
        df = df_full[df_full["year"] == year].copy()
        if df.empty:
            continue

        # 再生数の「上位％」を計算
        df['top_percentile'] = (1 - df['viewCounter'].rank(pct=True)) * 100
        
        df['p_bin'] = pd.cut(df['top_percentile'], bins=percentile_bins, include_lowest=True)
        grouped = df.groupby('p_bin', observed=False)
        median_length = grouped['lengthMinutes'].median()
        count_df = grouped['viewCounter'].count()
        
        valid_bins = count_df[count_df >= 10].index
        
        if not valid_bins.empty:
            plot_x = []
            plot_y = []
            for b in valid_bins:
                center = (b.left + b.right) / 2
                plot_x.append(center)
                plot_y.append(median_length[b])
            
            label = GENRE_MAP[genre_id]
            plt.plot(plot_x, plot_y, color=colors[i], marker='o', linestyle='-', 
                     linewidth=2.5, markersize=8, label=label, zorder=10)

    plt.xlim(100, 0)
    # 再生時間のY軸範囲はデータの様子を見て調整が必要かもしれないが、
    # 30分程度あれば十分か？ キッチンなどは長いかもしれない。
    # とりあえず自動スケールに任せるか、上限を設定するか。
    # いいね率は 0.15 だった。
    plt.ylim(0, None)
    
    plt.xlabel("ジャンル内の立ち位置（上位％）")
    plt.ylabel("再生時間の中央値 (分)")
    
    plt.title(f"ジャンル別 再生時間中央値の推移 (上位％基準, {year}年)")
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.legend(loc='lower center', ncol=3, frameon=True, facecolor='white', framealpha=0.9, fontsize=18)
    
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Generated length trends percentile comparison: {output_path}")

def plot_length_trends_yearly_per_genre():
    output_dir = Path("results/length")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    target_genres = [g for g in GENRE_ORDER if g != "software_talk"]
    target_years = [2020, 2023, 2025]
    
    percentile_bins = np.linspace(0, 100, 11)
    # ビンのラベル（中心値）
    bin_labels = [f"{int((percentile_bins[i] + percentile_bins[i+1])/2)}" for i in range(len(percentile_bins)-1)]
    
    for genre_id in target_genres:
        df_full = load_genre_data_raw(genre_id)
        if df_full is None:
            continue
            
        # ターゲット年のみ抽出
        df_target = df_full[df_full["year"].isin(target_years)].copy()
        if df_target.empty:
            continue

        # ジャンル内の各年ごとに上位％を計算
        dfs = []
        for year in target_years:
            df_year = df_target[df_target["year"] == year].copy()
            if df_year.empty:
                continue
            df_year['top_percentile'] = (1 - df_year['viewCounter'].rank(pct=True)) * 100
            df_year['p_bin'] = pd.cut(df_year['top_percentile'], bins=percentile_bins, include_lowest=True, labels=bin_labels)
            dfs.append(df_year)
        
        if not dfs:
            continue
            
        df_plot = pd.concat(dfs)
        
        plt.figure(figsize=(16, 10))
        
        # 箱ひげ図の描画
        sns.boxplot(
            data=df_plot, 
            x='p_bin', 
            y='lengthMinutes', 
            hue='year',
            palette="viridis",
            showfliers=False, # 外れ値を除去して見やすくする
            linewidth=2
        )

        # X軸を 100 -> 0 に見せるために反転
        plt.gca().invert_xaxis()
        
        plt.ylim(0, df_plot['lengthMinutes'].quantile(0.95)) # 上位5%を除外してスケールを調整
        
        plt.xlabel("ジャンル内の立ち位置（上位％）")
        plt.ylabel("再生時間 (分)")
        
        genre_name = GENRE_MAP[genre_id]
        plt.title(f"{genre_name}ジャンル 再生時間の分布推移 (2020, 2023, 2025)")
        plt.grid(True, axis='y', ls="-", alpha=0.2)
        plt.legend(title="年", loc='upper right', frameon=True, facecolor='white', framealpha=0.9)
        
        output_path = output_dir / f"length_dist_{genre_id}.png"
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()
        print(f"Generated yearly length boxplot for {genre_id}: {output_path}")

def plot_onboard_specific_years():
    output_dir = Path("results/length")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    genre_id = "onboard"
    target_years = [2018, 2020, 2023, 2025]
    colors = sns.color_palette("viridis", len(target_years))
    
    percentile_bins = np.linspace(0, 100, 11)
    
    df_full = load_genre_data_raw(genre_id)
    if df_full is None:
        return
        
    plt.figure(figsize=(14, 10))
    
    for i, year in enumerate(target_years):
        df = df_full[df_full["year"] == year].copy()
        if df.empty:
            continue

        df['top_percentile'] = (1 - df['viewCounter'].rank(pct=True)) * 100
        df['p_bin'] = pd.cut(df['top_percentile'], bins=percentile_bins, include_lowest=True)
        grouped = df.groupby('p_bin', observed=False)
        median_length = grouped['lengthMinutes'].median()
        count_df = grouped['viewCounter'].count()
        
        valid_bins = count_df[count_df >= 5].index
        
        if not valid_bins.empty:
            plot_x = []
            plot_y = []
            for b in valid_bins:
                center = (b.left + b.right) / 2
                plot_x.append(center)
                plot_y.append(median_length[b])
            
            plt.plot(plot_x, plot_y, color=colors[i], marker='o', linestyle='-', 
                     linewidth=2.5, markersize=8, label=f"{year}年", zorder=10)

    plt.xlim(100, 0)
    plt.ylim(0, None)
    
    plt.xlabel("ジャンル内の立ち位置（上位％）")
    plt.ylabel("再生時間の中央値 (分)")
    
    genre_name = GENRE_MAP[genre_id]
    plt.title(f"{genre_name}ジャンル 再生時間中央値の推移 (2018, 2020, 2023, 2025)")
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.legend(loc='best', frameon=True, facecolor='white', framealpha=0.9)
    
    output_path = output_dir / f"length_trends_onboard_specific.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Generated specific onboard length trends: {output_path}")

if __name__ == "__main__":
    plot_length_trends_comparison_percentile(2025)
    plot_length_trends_yearly_per_genre()
    plot_onboard_specific_years()
