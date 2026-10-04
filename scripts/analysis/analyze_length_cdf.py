# /// script
# dependencies = [
#   "matplotlib",
#   "matplotlib-fontja",
#   "pandas",
#   "seaborn",
#   "numpy",
# ]
# ///

import datetime
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
        print(f"Error: {pickle_path} not found.")
        return None
        
    with open(pickle_path, "rb") as f:
        recv = pickle.load(f)
    df = pd.json_normalize(recv["data"])

    # ソフトウェアトークの場合、VOCALOID関連を除外（歌唱系が混じるため）
    if category == "software_talk":
        df = filter_software_talk(df)

    df["startTime"] = pd.to_datetime(df["startTime"])
    df = df.sort_values("startTime", ignore_index=True)
    df.fillna({"userId": 0}, inplace=True)
    df["userId"] = df["userId"].astype("uint64")
    
    # 秒を分に変換
    df["lengthMinutes"] = df["lengthSeconds"] / 60.0
    return df

def visualize_cdf(df: pd.DataFrame, category: str, title: str, output_dir: Path, x_limit: float = None):
    print(f"Plotting Length CDF for {category} (Limit: {x_limit} min)...")
    df2 = df[["startTime", "lengthMinutes"]].copy()
    df2["year"] = df2["startTime"].dt.year
    
    # 年のフィルタリング
    if category == "game":
        target_years = [2014, 2017, 2020, 2023, 2024, 2025]
    elif category == "onboard":
        target_years = [2016, 2017, 2018, 2021, 2023, 2024, 2025]
    elif category == "travel":
        # 2018を削除し、2020, 2021を追加
        target_years = [2020, 2021, 2023, 2024, 2025]
    elif category == "theater":
        # 2021を削除し、2020を追加
        target_years = [2018, 2020, 2023, 2024, 2025]
    elif category == "kitchen":
        # 2018, 2021を削除し、2020を追加
        target_years = [2020, 2023, 2024, 2025]
    else:
        target_years = [2018, 2021, 2023, 2024, 2025]
    
    plt.figure(figsize=(12, 7))
    
    # 配色を調整
    colors = sns.color_palette("husl", len(target_years))
    
    for i, year in enumerate(target_years):
        year_data = df2[df2["year"] == year]["lengthMinutes"]
        if len(year_data) == 0:
            continue
            
        # 再生時間をソート
        sorted_lengths = np.sort(year_data.values)
        # 累積確率を計算 (0 to 1)
        cdf = np.arange(1, len(sorted_lengths) + 1) / len(sorted_lengths)
        
        plt.plot(sorted_lengths, cdf * 100, label=f"{year}年", color=colors[i], linewidth=2)

    if x_limit:
        plt.xlim(0, x_limit)
        suffix = f"_{x_limit}min"
    else:
        plt.xlim(0, None)
        suffix = "_unlimited"

    plt.xlabel("動画の長さ (分)")
    plt.ylabel("累積割合 (%)")
    plt.title(f"{title} - 動画長さの累積分布関数 (CDF)")
    plt.grid(True, which="both", linestyle="--", alpha=0.5)
    
    # 凡例をグラフの外側に配置
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # 0, 25, 50, 75, 100% の線を表示
    for h in [25, 50, 75]:
        plt.axhline(h, color='gray', linestyle=':', alpha=0.3)

    plt.tight_layout()
    
    output_path = output_dir / f"{category}_length_cdf{suffix}.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Saved: {output_path}")
    plt.close()

def main(category_arg=None):
    with open("config.toml", "rb") as f:
        cfg = tomllib.load(f)
    
    categories = [category_arg] if category_arg else cfg.keys()
    
    for category in categories:
        if category not in cfg:
            print(f"Category {category} not found in config.toml")
            continue
            
        output_dir = Path("results") / category
        output_dir.mkdir(parents=True, exist_ok=True)
        
        df = preprocess(category)
        if df is not None:
            # 制限版
            limit = 15 if category == "kitchen" else 30
            visualize_cdf(df, category, cfg[category]["title"], output_dir, x_limit=limit)
            
            # 車載(onboard)のみ、5分制限版も別途作成
            if category == "onboard":
                visualize_cdf(df, category, cfg[category]["title"], output_dir, x_limit=5)

            # 無制限版
            visualize_cdf(df, category, cfg[category]["title"], output_dir, x_limit=None)

if __name__ == "__main__":
    args = sys.argv
    if len(args) == 2:
        main(args[1])
    else:
        main()
