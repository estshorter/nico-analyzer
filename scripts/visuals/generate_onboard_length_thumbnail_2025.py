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

# グラフのスタイル設定
plt.rcParams['figure.dpi'] = 200

def load_genre_data(genre_id):
    input_path = Path(f"results/{genre_id}.pickle")
    if not input_path.exists():
        return None
    with open(input_path, "rb") as f:
        raw_data = pickle.load(f)
    data = raw_data["data"] if isinstance(raw_data, dict) else raw_data
    df = pd.DataFrame(data)
    df["startTime"] = pd.to_datetime(df["startTime"])
    df = df[df["startTime"].dt.year == 2025].copy()
    if df.empty: return None
    df["lengthMinutes"] = df["lengthSeconds"] / 60.0
    return df

def generate_onboard_length_thumbnail():
    output_dir = Path("results/thumbnail")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "thumbnail_length_onboard_2025_pure.png"

    plt.figure(figsize=(12, 8))

    # 車載ジャンル、2025年、色は視認性の高いサイバー・イエロー
    target = {"id": "onboard", "color": "#F1C40F"} # サイバー・イエロー

    percentile_bins = np.linspace(0, 100, 21)

    df = load_genre_data(target["id"])
    if df is None:
        print("Data not found.")
        return

    # 再生数の「上位％」を計算
    df['top_percentile'] = (1 - df['viewCounter'].rank(pct=True)) * 100
    df['p_bin'] = pd.cut(df['top_percentile'], bins=percentile_bins, include_lowest=True)

    grouped = df.groupby('p_bin', observed=False)
    median_length = grouped['lengthMinutes'].median()

    plot_x = []
    plot_y = []
    for b in grouped.groups.keys():
        if len(grouped.get_group(b)) >= 5:
            center = (b.left + b.right) / 2
            plot_x.append(center)
            plot_y.append(median_length[b])

    # 線を描画（マーカーなし、極太）
    plt.plot(plot_x, plot_y, color=target["color"], linestyle='-', linewidth=25)

    # 範囲の調整（元グラフを参考に、上位層に絞るか全体か）
    # 元グラフは 100 -> 0 で、2025年は 7m -> 10m くらい
    plt.xlim(95, 5) 
    plt.ylim(6, 12)

    # グリッド、軸、文字をすべて消す
    plt.grid(False)
    plt.axis('off')

    # 背景を透明に設定（黒背景に置く前提）
    plt.savefig(output_path, dpi=300, transparent=True, bbox_inches="tight", pad_inches=0)
    plt.close()
    print(f"Generated pure length thumbnail graph: {output_path}")

if __name__ == "__main__":
    generate_onboard_length_thumbnail()
