# /// script
# dependencies = [
#   "matplotlib",
#   "matplotlib-fontja",
#   "pandas",
#   "seaborn",
#   "numpy",
#   "scipy",
# ]
# ///

import pickle
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
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

def main():
    category = "onboard"
    year_target = 2025
    
    # フォント設定 (一応)
    plt.rcParams['figure.dpi'] = 200

    df = preprocess(category)
    if df is None:
        print(f"Data for {category} not found.")
        return
        
    year_data = df[df["year"] == year_target]["viewCounter"]
    year_data = year_data[year_data > 0]

    plt.figure(figsize=(12, 8))
    
    # 車載の緑色 (Dark2の最初の方)
    colors = plt.get_cmap("Dark2").colors
    color = colors[0] # 車載の色

    # KDEプロット
    sns.kdeplot(year_data, log_scale=True, color=color, linewidth=15, alpha=1.0)

    # 装飾をすべて消す
    ax = plt.gca()
    
    # タイトル、凡例、ラベルを消去
    plt.title("")
    plt.xlabel("")
    plt.ylabel("")
    
    # Y軸を非表示
    ax.get_yaxis().set_visible(False)
    
    # 軸の枠線を制御 (X軸の下線だけ残す)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_linewidth(2)
    ax.spines['bottom'].set_color('#333333')
    
    # 目盛り(tick)とラベルを非表示
    ax.xaxis.set_ticks([])
    
    # グリッドも非表示
    plt.grid(False)
    
    plt.xlim(10, 100000)
    
    plt.tight_layout()
    output_path = "results/onboard_thumbnail_simplified.png"
    plt.savefig(output_path, dpi=300, transparent=True)
    plt.close()
    
    print(f"Saved simplified onboard plot to {output_path}")

if __name__ == "__main__":
    main()
