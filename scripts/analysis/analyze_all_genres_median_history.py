# /// script
# dependencies = [
#   "matplotlib",
#   "matplotlib-fontja",
#   "pandas",
#   "numpy",
#   "seaborn",
#   "tabulate",
# ]
# ///

import pickle
import tomllib
from pathlib import Path
import matplotlib_fontja
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

def main():
    with open("config.toml", "rb") as f:
        cfg = tomllib.load(f)
    
    all_stats = []
    
    # software_talk を除外
    categories = [cat for cat in cfg.keys() if cat != "software_talk"]
    
    for category in categories:
        pickle_path = Path(f"results/{category}.pickle")
        if not pickle_path.exists():
            continue
            
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
        median_stats["category"] = category
        median_stats["title"] = cfg[category]["title"]
        all_stats.append(median_stats)
    
    if not all_stats:
        print("No data found.")
        return
        
    df_all = pd.concat(all_stats, ignore_index=True)
    
    # グラフ作成
    plt.figure(figsize=(12, 7))
    
    # Dark2 パレットを使用
    colors = sns.color_palette("Dark2", n_colors=len(categories))
    
    for i, category in enumerate(categories):
        cat_data = df_all[df_all["category"] == category]
        if cat_data.empty:
            continue
        
        plt.plot(cat_data["year"], cat_data["lengthMinutes"], 
                 marker='o', linewidth=3, label=cfg[category]["title"], color=colors[i])

    plt.xlabel("年")
    plt.ylabel("再生時間の中央値 (分)")
    plt.title("各ジャンルの動画再生時間の中央値推移 (2020-2025)")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    output_dir = Path("results")
    output_path = output_dir / "all_genres_median_history_2020_2025.png"
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Saved: {output_path}")
    
    # テキスト出力用
    pivot_df = df_all.pivot(index="year", columns="title", values="lengthMinutes")
    print("\n再生時間の中央値 (分):")
    print(pivot_df.to_markdown())

if __name__ == "__main__":
    main()
