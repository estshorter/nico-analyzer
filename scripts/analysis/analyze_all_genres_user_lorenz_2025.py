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
    
    if "userId" in df.columns:
        df["userId"] = df["userId"].fillna(0).astype("uint64")
    else:
        df["userId"] = 0
    return df

def calculate_gini(values):
    """ジニ係数を計算する"""
    if len(values) == 0:
        return 0
    sorted_values = np.sort(values)
    n = len(values)
    index = np.arange(1, n + 1)
    return (2 * np.sum(index * sorted_values) / (n * np.sum(sorted_values))) - (n + 1) / n

def main():
    with open("config.toml", "rb") as f:
        cfg = tomllib.load(f)
    
    # ソフトウェアトーク全体を除外
    categories = [cat for cat in cfg.keys() if cat != "software_talk"]
    
    year_target = 2025
    
    # データの準備
    plot_data = []
    for category in categories:
        df = preprocess(category)
        if df is None: continue
        
        year_data = df[df["year"] == year_target]
        if len(year_data) == 0: continue
        
        # ユーザー別に集計
        user_views = year_data.groupby("userId")["viewCounter"].sum().values
        sorted_views = np.sort(user_views)
        gini = calculate_gini(sorted_views)
        
        n = len(sorted_views)
        x_lorenz = np.arange(0, n + 1) / n
        y_lorenz = np.insert(np.cumsum(sorted_views), 0, 0)
        y_lorenz = y_lorenz / y_lorenz[-1]
        
        label_base = cfg[category]["title"].replace("ニコニコ ", "").replace(" 年次統計", "")
        plot_data.append({
            "category": category,
            "label": f"{label_base} (Gini: {gini:.3f})",
            "x": x_lorenz * 100,
            "y": y_lorenz * 100,
            "gini": gini
        })

    if not plot_data:
        print("No data found for 2025.")
        return

    # ジニ係数が低い（平等に近い）順にソートして、色を割り当て
    plot_data.sort(key=lambda x: x["gini"])

    colors = plt.get_cmap("Dark2").colors

    # --- ユーザー別 ローレンツ曲線 比較グラフ ---
    plt.figure(figsize=(9, 9))
    plt.plot([0, 100], [0, 100], 'k--', label="完全均等分配線", alpha=0.6, linewidth=1.5)
    
    for i, data in enumerate(plot_data):
        plt.plot(data["x"], data["y"], label=data["label"], color=colors[i % 8], 
                 linewidth=3, alpha=1.0)

    plt.xlabel("クリエイター（投稿者）の累積割合 (下位からの累積 %)")
    plt.ylabel("年間総再生数の累積割合 (%)")
    plt.title(f"{year_target}年 ジャンル別クリエイター寡占度 (ユーザー別ローレンツ曲線)")
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.legend(loc='upper left', frameon=True, shadow=True)
    plt.tight_layout()
    
    output_dir = Path("results/cdf_lorenz")
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "all_genres_user_lorenz_2025_refined.png"
    
    plt.savefig(out_path, dpi=300)
    plt.close()
    
    print(f"Saved refined user lorenz plots to {out_path}")

if __name__ == "__main__":
    main()
