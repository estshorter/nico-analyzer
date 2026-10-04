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

    output_dir = Path(f"results/{category}")
    output_dir.mkdir(parents=True, exist_ok=True)

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
    
    for year in years:
        year_data = df[df["year"] == year]["lengthSeconds"]
        year_data = year_data[year_data > 0]
        
        if year_data.empty:
            print(f"No data for {year}")
            continue

        plt.figure(figsize=(12, 8))
        sns.kdeplot(year_data, log_scale=True, color="C0", linewidth=4, fill=True, alpha=0.3)

        plt.gca().xaxis.set_major_formatter(log_formatter)
        plt.gca().xaxis.set_major_locator(ticker.LogLocator(base=10, subs=[1.0, 2.0, 3.0, 5.0]))
        
        plt.xlabel("再生時間")
        plt.ylabel("密度 (Density)")
        plt.title(f"{year}年 ニコニコ車載動画 再生時間分布")
        plt.grid(True, which="both", linestyle="--", alpha=0.4)
        
        plt.xlim(10, 7200) # 10秒から2時間
        
        plt.tight_layout()
        output_path = output_dir / f"length_distribution_{year}.png"
        plt.savefig(output_path, dpi=300)
        plt.close()
        print(f"Saved {output_path}")

if __name__ == "__main__":
    main()
