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
plt.rcParams['font.size'] = 16
plt.rcParams['axes.titlesize'] = 24
plt.rcParams['axes.labelsize'] = 20
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['legend.fontsize'] = 16
plt.rcParams['xtick.labelsize'] = 16
plt.rcParams['ytick.labelsize'] = 16
plt.rcParams['figure.dpi'] = 200

# ジャンルの日本語名マッピング
GENRE_MAP = {
    "software_talk": "ボイロ全体"
}

def load_data(file_name, is_software_talk=False):
    input_path = Path(f"results/{file_name}.pickle")
    if not input_path.exists():
        print(f"File not found: {input_path}")
        return None

    with open(input_path, "rb") as f:
        raw_data = pickle.load(f)
    
    if isinstance(raw_data, dict) and "data" in raw_data:
        data = raw_data["data"]
    else:
        data = raw_data

    if isinstance(data, list):
        df = pd.DataFrame(data)
    elif isinstance(data, pd.DataFrame):
        df = data
    else:
        return None
        
    if is_software_talk:
        df = filter_software_talk(df)

    df["startTime"] = pd.to_datetime(df["startTime"])
    df = df[df["startTime"].dt.year == 2025].copy()
    
    df = df[df["viewCounter"] > 0].copy()
    df["likeRatio"] = df["likeCounter"] / df["viewCounter"]
    
    return df

def plot_pure_scatter(file_name, is_software_talk=False):
    df = load_data(file_name, is_software_talk=is_software_talk)
    if df is None:
        return

    output_dir = Path("results/like_ratio_pure")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"like_ratio_{file_name}_pure.png"
    
    plt.figure(figsize=(12, 8))
    
    # 散布図のみを描画
    color = "darkorange" if is_software_talk else "steelblue"
    sns.scatterplot(data=df, x="viewCounter", y="likeRatio", 
                    color=color, alpha=0.5, s=30)

    plt.xscale("log")
    plt.xlim(1, 10**6)
    plt.ylim(0, 0.5)
    
    plt.xlabel("再生数")
    plt.ylabel("いいね率 (%)")
    plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x*100:g}'))
    
    genre_jp = GENRE_MAP.get(file_name, "ボイロ全体")
    plt.title(f"再生数 vs いいね率 (2025年) - {genre_jp}")
    plt.grid(True, which="both", ls="-", alpha=0.2)
    
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Generated pure scatter plot: {output_path}")

if __name__ == "__main__":
    plot_pure_scatter("software_talk", is_software_talk=True)
