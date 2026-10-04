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

import matplotlib_fontja
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import numpy as np
import seaborn as sns

def main():
    category = "onboard"
    pickle_path = Path(f"results/{category}.pickle")
    if not pickle_path.exists():
        print(f"Error: {pickle_path} not found")
        return
        
    with open(pickle_path, "rb") as f:
        recv = pickle.load(f)
    df = pd.json_normalize(recv["data"])
    df["startTime"] = pd.to_datetime(df["startTime"])
    df["year"] = df["startTime"].dt.year
    df["lengthSeconds"] = df["lengthSeconds"].astype(float)

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

    def time_formatter(x, pos):
        if x < 60:
            return f'{int(x)}s'
        elif x < 3600:
            return f'{int(x/60)}m'
        else:
            return f'{int(x/3600)}h'

    log_formatter = ticker.FuncFormatter(time_formatter)

    years = range(2021, 2026)
    colors = plt.get_cmap("viridis")(np.linspace(0, 0.8, len(years))) # グラデーション

    plt.figure(figsize=(12, 8))
    
    for i, year in enumerate(years):
        year_data = df[df["year"] == year]["lengthSeconds"]
        year_data = year_data[year_data > 0]
        
        if year_data.empty:
            continue

        sns.kdeplot(year_data, log_scale=True, label=f"{year}年", 
                    color=colors[i], linewidth=4, alpha=0.7)

    plt.gca().xaxis.set_major_formatter(log_formatter)
    plt.gca().xaxis.set_major_locator(ticker.LogLocator(base=10, subs=[1.0, 2.0, 3.0, 5.0]))
    
    plt.xlabel("再生時間")
    plt.ylabel("密度 (Density)")
    plt.title("ニコニコ車載動画 再生時間分布の推移 (2021-2025)")
    plt.grid(True, which="both", linestyle="--", alpha=0.4)
    plt.legend(loc='upper right', frameon=True)
    
    plt.xlim(10, 7200) # 10秒から2時間
    
    plt.tight_layout()
    output_path = Path("results/onboard/length_distribution_history_combined.png")
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Saved combined distribution plot to {output_path}")

if __name__ == "__main__":
    main()
