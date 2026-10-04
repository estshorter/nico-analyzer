# /// script
# dependencies = [
#   "matplotlib",
#   "matplotlib-fontja",
#   "pandas",
#   "numpy",
# ]
# ///

import pickle
import tomllib
from pathlib import Path
import matplotlib_fontja
import matplotlib.pyplot as plt
import pandas as pd

def main():
    category = "kitchen"
    pickle_path = Path(f"results/{category}.pickle")
    if not pickle_path.exists():
        print(f"Error: {pickle_path} not found.")
        return
        
    with open(pickle_path, "rb") as f:
        recv = pickle.load(f)
    df = pd.json_normalize(recv["data"])

    df["startTime"] = pd.to_datetime(df["startTime"])
    df["year"] = df["startTime"].dt.year
    df["lengthMinutes"] = df["lengthSeconds"] / 60.0

    # 2020年以降を抽出
    df_filtered = df[df["year"] >= 2020].copy()
    
    # 年ごとの中央値を計算
    median_stats = df_filtered.groupby("year")["lengthMinutes"].median().reset_index()
    
    # グラフ作成
    plt.figure(figsize=(10, 6))
    bars = plt.bar(median_stats["year"], median_stats["lengthMinutes"], color="skyblue", edgecolor="navy")
    
    # 数値を表示
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 0.1, f"{yval:.2f}分", ha="center", va="bottom", fontsize=10)

    plt.xlabel("年")
    plt.ylabel("再生時間の中央値 (分)")
    plt.ylim(0, 4.5)
    plt.title("料理カテゴリ - 動画再生時間の中央値推移 (2020-2025)")
    plt.xticks(median_stats["year"])
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    
    output_dir = Path("results") / category
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "kitchen_median_history_2020_2025.png"
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    print(f"Saved: {output_path}")
    plt.close()

if __name__ == "__main__":
    main()
