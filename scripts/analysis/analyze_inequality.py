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
import sys
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
    return (2 * np.sum(index * sorted_values) / (n * np.sum(sorted_values))) - (n + 1) / n

def visualize_cdf_limited(df, category, title, output_dir, target_years=[2018, 2023, 2025]):
    plt.figure(figsize=(10, 6))
    # Dark2 カラーパレットを使用
    colors = plt.get_cmap("Dark2").colors
    
    for i, year in enumerate(target_years):
        year_data = df[df["year"] == year]["viewCounter"]
        if len(year_data) == 0: continue
        sorted_views = np.sort(year_data.values)
        cdf = np.arange(1, len(sorted_views) + 1) / len(sorted_views)
        plt.plot(np.maximum(sorted_views, 1), cdf * 100, label=f"{year}年", 
                 color=colors[i % 8], linewidth=3, alpha=1.0)

    plt.xscale("log")
    plt.xlabel("再生数 (対数軸)")
    plt.ylabel("累積割合 (%)")
    plt.title(f"{title} - 再生数累積分布 (CDF)")
    plt.grid(True, which="both", linestyle="--", alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / f"{category}_view_cdf_limited.png", dpi=300)
    plt.close()

def visualize_lorenz(df, category, title, output_dir, target_years=[2018, 2021, 2025]):
    plt.figure(figsize=(8, 8))
    # Dark2 カラーパレットを使用
    colors = plt.get_cmap("Dark2").colors
    
    # 均等分配線
    plt.plot([0, 100], [0, 100], 'k--', label="完全均等分配線", alpha=0.5)
    
    gini_results = {}

    for i, year in enumerate(target_years):
        year_data = df[df["year"] == year]["viewCounter"]
        if len(year_data) == 0: continue
        
        sorted_views = np.sort(year_data.values)
        n = len(sorted_views)
        
        # 累積個数割合
        x_lorenz = np.arange(0, n + 1) / n
        # 累積再生数割合
        y_lorenz = np.insert(np.cumsum(sorted_views), 0, 0)
        y_lorenz = y_lorenz / y_lorenz[-1]
        
        gini = calculate_gini(sorted_views)
        gini_results[year] = gini
        
        plt.plot(x_lorenz * 100, y_lorenz * 100, label=f"{year}年 (Gini: {gini:.3f})", 
                 color=colors[i % 8], linewidth=3, alpha=1.0)

    plt.xlabel("動画の累積割合 (下位からの累積 %)")
    plt.ylabel("再生数の累積割合 (%)")
    plt.title(f"{title} - ローレンツ曲線")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / f"{category}_lorenz.png", dpi=300)
    plt.close()
    return gini_results

def main():
    with open("config.toml", "rb") as f:
        cfg = tomllib.load(f)
    
    all_gini_data = []
    target_years = [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]

    for category in cfg.keys():
        output_dir = Path("results") / category
        output_dir.mkdir(parents=True, exist_ok=True)
        
        df = preprocess(category)
        if df is not None:
            visualize_cdf_limited(df, category, cfg[category]["title"], output_dir, target_years)
            gini_dict = visualize_lorenz(df, category, cfg[category]["title"], output_dir, target_years)
            
            row = {"Genre": cfg[category]["title"]}
            for year in target_years:
                row[year] = gini_dict.get(year, np.nan)
            all_gini_data.append(row)

    # Markdown出力
    gini_df = pd.DataFrame(all_gini_data)
    # 年の列を文字列に変換してフォーマット
    for year in target_years:
        if year in gini_df.columns:
            gini_df[year] = gini_df[year].map(lambda x: f"{x:.3f}" if pd.notnull(x) else "-")
    
    md_content = "## ジャンル別ジニ係数 推移\n\n"
    md_content += gini_df.to_markdown(index=False)
    
    print("\n" + md_content)
    
    # ファイル保存
    output_md_path = Path("results/gini_coefficients.md")
    with open(output_md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"\nSaved Markdown table to: {output_md_path}")

if __name__ == "__main__":
    main()
