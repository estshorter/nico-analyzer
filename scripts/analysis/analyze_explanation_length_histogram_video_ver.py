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
import matplotlib_fontja
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np

def preprocess(category):
    pickle_path = Path(f"results/{category}.pickle")
    if not pickle_path.exists():
        return None
    with open(pickle_path, "rb") as f:
        recv = pickle.load(f)
    df = pd.json_normalize(recv["data"])
    df["startTime"] = pd.to_datetime(df["startTime"])
    df["year"] = df["startTime"].dt.year
    df["lengthSeconds"] = df["lengthSeconds"].astype(float)
    return df

def main():
    category = "explanation"
    label = "解説"
    target_years = [2024, 2025]
    
    df = preprocess(category)
    if df is None: return

    # 1分単位のデータを集計
    plot_data = []
    for year in target_years:
        year_data = df[df["year"] == year]["lengthSeconds"] / 60.0
        # 0分から10分までの各分ごとの本数をカウント
        for m in range(10):
            count = len(year_data[(year_data >= m) & (year_data < m + 1)])
            plot_data.append({"年": f"{year}年", "再生時間": f"{m}-{m+1}分", "動画数": count, "minute": m})

    pdf = pd.DataFrame(plot_data)

    # グラフ設定 (video_length_history_graph.png を参考にした太字・大文字設定)
    plt.rcParams['font.family'] = ['IBM Plex Sans JP', 'BIZ UDGothic', 'Yu Gothic', 'Meiryo', 'MS Gothic', 'sans-serif']
    plt.rcParams['font.weight'] = 'bold'
    plt.rcParams['font.size'] = 18
    plt.rcParams['axes.titlesize'] = 32
    plt.rcParams['axes.labelsize'] = 24
    plt.rcParams['axes.labelweight'] = 'bold'
    plt.rcParams['axes.titleweight'] = 'bold'
    plt.rcParams['legend.fontsize'] = 20
    plt.rcParams['xtick.labelsize'] = 18
    plt.rcParams['ytick.labelsize'] = 18
    plt.rcParams['figure.dpi'] = 200

    plt.figure(figsize=(16, 9))
    
    # 並び型の棒グラフ
    colors = ["#7fbf7f", "#7f7fdf"] # 緑(2024)、青(2025)
    ax = sns.barplot(data=pdf, x="再生時間", y="動画数", hue="年", palette=colors, edgecolor="white", linewidth=1)

    plt.xlabel("再生時間 (分)", labelpad=15)
    plt.ylabel("動画投稿数 (本)", labelpad=15)
    plt.title(f"{label}ジャンル 再生時間別の推移 (2023-2025)", pad=30)
    
    plt.grid(True, axis='y', linestyle='--', alpha=0.5)
    plt.legend(loc='upper right', frameon=True)
    
    # 軸のカンマ区切り
    from matplotlib.ticker import FuncFormatter
    plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda x, p: format(int(x), ',')))

    plt.tight_layout()
    output_path = f"results/{category}/{category}_length_histogram_video_ver.png"
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Saved: {output_path}")

if __name__ == "__main__":
    main()
