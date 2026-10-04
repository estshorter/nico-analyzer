# /// script
# dependencies = [
#   "matplotlib",
#   "matplotlib-fontja",
#   "pandas",
#   "seaborn",
#   "numpy",
#   "scipy",
#   "tabulate",
# ]
# ///

import pickle
import sys
import tomllib
from pathlib import Path
import matplotlib_fontja
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import numpy as np
import seaborn as sns
from scipy.stats import norm

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

def main():
    with open("config.toml", "rb") as f:
        cfg = tomllib.load(f)
    
    # フォント設定：IBM Plex Sans JP を優先（太字設定）
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

    # 対数軸の目盛りを数値表記（10, 100, 1000...）にするためのフォーマッタ
    log_formatter = ticker.FuncFormatter(lambda x, pos: f'{int(x):,}' if x >= 1 else f'{x}')

    # Use Dark2 colormap
    colors = plt.get_cmap("Dark2").colors
    
    # グリッドのスタイルを定義
    grid_style_base = {
        'color': '#b0b0b0', 
        'alpha': 0.7,
        'linewidth': 1.0
    }
    
    # 補助線用のスタイル（グリッドに合わせつつ破線にする）
    threshold_style = {
        **grid_style_base,
        'linestyle': '--'
    }
    
    # 1. Onboard (車載) CDF Graphs
    df_onboard = preprocess("onboard")
    if df_onboard is not None:
        # 1-1: 2025 only
        plt.figure(figsize=(12, 8))
        data_2025 = df_onboard[df_onboard["year"] == 2025]["viewCounter"]
        sorted_views = np.sort(data_2025.values)
        cdf = np.arange(1, len(sorted_views) + 1) / len(sorted_views)
        
        plt.plot(np.maximum(sorted_views, 1), cdf * 100, color=colors[0], linewidth=4, label="2025年")
        plt.xscale("log")
        plt.gca().xaxis.set_major_formatter(log_formatter)
        plt.xlim(10, 10**5)
        plt.xlabel("再生数 (対数軸)")
        plt.ylabel("累積割合 (%)")
        plt.title("ボイロ車載動画 再生数累積分布")
        
        plt.axhline(50, **threshold_style)
        plt.axhline(70, **threshold_style)
        
        plt.grid(True, which="major", axis="y", linestyle='-', color=grid_style_base['color'], alpha=grid_style_base['alpha'], linewidth=grid_style_base['linewidth'])
        plt.grid(True, which="both", axis="x", linestyle="--", alpha=0.4)
        
        plt.legend(loc='upper left', frameon=True, shadow=False)
        plt.savefig("results/onboard/onboard_view_cdf_limited.png", dpi=300, bbox_inches="tight", transparent=False)
        plt.close()

        # 1-2: 2025, 2022, 2018 comparison
        plt.figure(figsize=(12, 8))
        years = [2025, 2022, 2018]
        for i, year in enumerate(years):
            data_year = df_onboard[df_onboard["year"] == year]["viewCounter"]
            sorted_views = np.sort(data_year.values)
            cdf = np.arange(1, len(sorted_views) + 1) / len(sorted_views)
            plt.plot(np.maximum(sorted_views, 1), cdf * 100, color=colors[i % len(colors)], linewidth=4, label=f"{year}年")
        
        plt.xscale("log")
        plt.gca().xaxis.set_major_formatter(log_formatter)
        plt.xlim(10, 10**5)
        plt.xlabel("再生数 (対数軸)")
        plt.ylabel("累積割合 (%)")
        plt.title("ボイロ車載動画 再生数累積分布")
        
        plt.axhline(50, **threshold_style)
        plt.axhline(70, **threshold_style)
        
        plt.legend(loc='upper left', frameon=True, shadow=False)
        plt.grid(True, which="major", axis="y", linestyle='-', color=grid_style_base['color'], alpha=grid_style_base['alpha'], linewidth=grid_style_base['linewidth'])
        plt.grid(True, which="both", axis="x", linestyle="--", alpha=0.4)
        plt.savefig("results/onboard/onboard_view_cdf_comparison.png", dpi=300, bbox_inches="tight", transparent=False)
        plt.close()

        # 2. Onboard Median History (Bar Chart)
        plt.figure(figsize=(12, 8))
        median_history = []
        target_years = range(2018, 2026)
        for year in target_years:
            data_year = df_onboard[df_onboard["year"] == year]["viewCounter"]
            median_history.append(np.median(data_year) if len(data_year) > 0 else 0)
        
        plt.bar(target_years, median_history, color=colors[2], alpha=0.85, edgecolor='white', linewidth=1.5)
        plt.ylim(0, max(median_history) * 1.2)
        plt.xlabel("年")
        plt.ylabel("再生数中央値")
        plt.title("ボイロ車載動画 再生数中央値の推移")
        for i, v in enumerate(median_history):
            plt.text(target_years[i], v + 10, f"{int(v):,}", ha='center', fontsize=20, fontweight='bold')
        plt.savefig("results/onboard/onboard_median_history.png", dpi=300, bbox_inches="tight", transparent=False)
        plt.close()

    # 3. All-Genre 2025 CDF Graph
    genre_map = {"game": "実況", "theater": "劇場", "explanation": "解説", "kitchen": "キッチン", "onboard": "車載", "travel": "旅行"}
    categories = ["game", "theater", "explanation", "kitchen", "onboard", "travel"]
    
    plt.figure(figsize=(12, 8))
    t_scores = []
    medians_2025 = {}

    for i, cat in enumerate(categories):
        df = preprocess(cat)
        if df is None: continue
        data_2025 = df[df["year"] == 2025]["viewCounter"]
        if len(data_2025) == 0: continue
        sorted_views = np.sort(data_2025.values)
        cdf = np.arange(1, len(sorted_views) + 1) / len(sorted_views)
        plt.plot(np.maximum(sorted_views, 1), cdf * 100, color=colors[i % len(colors)], linewidth=4, label=genre_map[cat])
        medians_2025[genre_map[cat]] = np.median(data_2025)

        for year in [2018, 2025]:
            year_data = df[df["year"] == year]["viewCounter"]
            if len(year_data) > 0:
                count_le_1000 = np.sum(year_data <= 1000)
                cdf_val = count_le_1000 / len(year_data)
                p = np.clip(cdf_val, 0.0001, 0.9999)
                z_score = norm.ppf(p)
                t_score = 50 + (z_score * 10)
                t_scores.append({"Genre": genre_map[cat], "Year": year, "CDF at 1000 (%)": cdf_val * 100, "T-Score": t_score})

    plt.xscale("log")
    plt.gca().xaxis.set_major_formatter(log_formatter)
    plt.xlim(10, 10**5)
    plt.xlabel("再生数 (対数軸)")
    plt.ylabel("累積割合 (%)")
    plt.title("2025年 ジャンル別 再生数累積分布")
    
    plt.axhline(50, **threshold_style)
    plt.axhline(70, **threshold_style)
    
    plt.grid(True, which="major", axis="y", linestyle='-', color=grid_style_base['color'], alpha=grid_style_base['alpha'], linewidth=grid_style_base['linewidth'])
    plt.grid(True, which="both", axis="x", linestyle="--", alpha=0.4)
    plt.legend(loc='upper left', frameon=True, shadow=False)
    plt.tight_layout()
    plt.savefig("results/all_genres_view_cdf_2025_refined.png", dpi=300, bbox_inches="tight", transparent=False)
    plt.close()

    # --- 3-2. Highlight Graphs ---
    for highlight_target in ["game", "kitchen"]:
        plt.figure(figsize=(12, 8))
        for i, cat in enumerate(categories):
            df = preprocess(cat)
            if df is None: continue
            data_2025 = df[df["year"] == 2025]["viewCounter"]
            if len(data_2025) == 0: continue
            
            sorted_views = np.sort(data_2025.values)
            cdf = np.arange(1, len(sorted_views) + 1) / len(sorted_views)
            
            if cat == highlight_target:
                color = colors[i % len(colors)]
                linewidth = 5
                alpha = 1.0
                zorder = 10
            else:
                color = "#d1d5db" # Gray
                linewidth = 2
                alpha = 0.4
                zorder = 1
                
            plt.plot(np.maximum(sorted_views, 1), cdf * 100, color=color, linewidth=linewidth, alpha=alpha, zorder=zorder, label=genre_map[cat])

        plt.xscale("log")
        plt.gca().xaxis.set_major_formatter(log_formatter)
        plt.xlim(10, 10**5)
        plt.xlabel("再生数 (対数軸)")
        plt.ylabel("累積割合 (%)")
        plt.title(f"2025年 ジャンル別 再生数累積分布 ({genre_map[highlight_target]}ハイライト)")
        
        plt.axhline(50, **threshold_style)
        plt.axhline(70, **threshold_style)
        
        plt.grid(True, which="major", axis="y", linestyle='-', color=grid_style_base['color'], alpha=grid_style_base['alpha'], linewidth=grid_style_base['linewidth'])
        plt.grid(True, which="both", axis="x", linestyle="--", alpha=0.4)
        plt.legend(loc='upper left', frameon=True, shadow=False)
        plt.tight_layout()
        plt.savefig(f"results/all_genres_view_cdf_2025_highlight_{highlight_target}.png", dpi=300, bbox_inches="tight", transparent=False)
        plt.close()

    # 4. All-Genre Median 2025 Horizontal Bar Chart
    plt.figure(figsize=(12, 8))
    sorted_medians = sorted(medians_2025.items(), key=lambda x: x[1], reverse=True)
    genre_names = [x[0] for x in sorted_medians]
    median_values = [x[1] for x in sorted_medians]
    
    # 順序を反転（barhは下から描画するため）
    genre_names = genre_names[::-1]
    median_values = median_values[::-1]
    
    bars = plt.barh(genre_names, median_values, color=colors[:len(genre_names)][::-1], edgecolor='black', linewidth=1.5)
    
    plt.title('2025年 ジャンル別 再生数中央値', pad=25, fontweight='bold')
    plt.xlabel('再生数中央値', labelpad=15, fontweight='bold')
    plt.ylabel('ジャンル', labelpad=15, fontweight='bold')
    plt.xlim(0, max(median_values) * 1.2)
    
    for bar in bars:
        width = bar.get_width()
        plt.text(width + 20, bar.get_y() + bar.get_height()/2, f'{int(width):,}', va='center', fontsize=18, fontweight='bold')
    
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.savefig("results/all_genres_median_2025.png", dpi=300, bbox_inches="tight", transparent=False)
    plt.close()

    t_scores_df = pd.DataFrame(t_scores)
    md_output = "## 1000再生の偏差値 (T-Score) 比較\n\n"
    md_output += t_scores_df.to_markdown(index=False)
    with open("results/genre_t_scores_1000_views.md", "w", encoding="utf-8") as f:
        f.write(md_output)

    print("Successfully generated all graphs with white background.")

if __name__ == "__main__":
    main()
