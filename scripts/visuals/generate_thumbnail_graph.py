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
    df = df[df["viewCounter"] > 0].copy()
    df["likeRatio"] = df["likeCounter"] / df["viewCounter"]
    return df

def generate_thumbnail_graph():
    output_dir = Path("results/thumbnail")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "thumbnail_graph_city_vs_village_pure.png"
    
    plt.figure(figsize=(12, 8))
    
    # 比較対象のジャンル（村＝車載、都会＝ゲーム）
    targets = [
        {"id": "onboard", "color": "#2ECC71"}, # 緑
        {"id": "game", "color": "#3498DB"}    # 青
    ]
    
    percentile_bins = np.linspace(0, 100, 21)
    
    for target in targets:
        df = load_genre_data(target["id"])
        if df is None: continue
            
        df['top_percentile'] = (1 - df['viewCounter'].rank(pct=True)) * 100
        df['p_bin'] = pd.cut(df['top_percentile'], bins=percentile_bins, include_lowest=True)
        
        grouped = df.groupby('p_bin', observed=False)
        median_like_ratio = grouped['likeRatio'].median()
        
        plot_x = []
        plot_y = []
        for b in grouped.groups.keys():
            if len(grouped.get_group(b)) >= 5:
                center = (b.left + b.right) / 2
                plot_x.append(center)
                plot_y.append(median_like_ratio[b])
        
        # 線を描画（マーカーなし、極太）
        plt.plot(plot_x, plot_y, color=target["color"], linestyle='-', linewidth=25)

    # 指定の範囲に調整
    plt.xlim(85, 15)
    plt.ylim(0.05, 0.15)
    
    # グリッド、軸、文字をすべて消す
    plt.grid(False)
    plt.axis('off')
    
    # 背景を白に設定（必要なら透明も可）
    plt.savefig(output_path, dpi=300, transparent=True, bbox_inches="tight", pad_inches=0)
    plt.close()
    print(f"Generated pure thumbnail graph: {output_path}")

if __name__ == "__main__":
    generate_thumbnail_graph()
