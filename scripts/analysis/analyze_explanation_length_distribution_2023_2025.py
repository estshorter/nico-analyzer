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
import pandas as pd
import seaborn as sns

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
    target_years = [2023, 2024, 2025]
    
    plt.rcParams['font.family'] = ['IBM Plex Sans JP', 'BIZ UDGothic', 'Yu Gothic', 'Meiryo', 'MS Gothic', 'sans-serif']
    plt.rcParams['font.weight'] = 'bold'
    plt.rcParams['font.size'] = 16
    plt.rcParams['figure.dpi'] = 200

    plt.figure(figsize=(12, 8))
    
    df = preprocess(category)
    if df is None:
        print(f"Error: {category}.pickle not found.")
        return

    colors = sns.color_palette("husl", len(target_years))

    for i, year in enumerate(target_years):
        year_data = df[df["year"] == year]["lengthSeconds"]
        if year_data.empty:
            print(f"Warning: No data for year {year}")
            continue
            
        year_data_min = year_data / 60.0 # 分に変換
        
        sns.kdeplot(year_data_min, label=f"{year}年", 
                    color=colors[i], linewidth=4, alpha=0.8)

    plt.xlabel("再生時間 (分)")
    plt.ylabel("密度 (Density)")
    plt.title(f"{label}ジャンル 再生時間分布の推移 (2023-2025)")
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.legend(loc='upper right')
    
    plt.xlim(0, 10) # 0分から10分に限定
    plt.xticks(range(0, 11, 1)) # 1分おきに目盛り
    
    plt.tight_layout()
    output_path = f"results/{category}/{category}_length_distribution_2023_2025.png"
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Saved: {output_path}")

if __name__ == "__main__":
    main()
