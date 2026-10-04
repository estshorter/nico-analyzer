# /// script
# dependencies = [
#   "matplotlib",
#   "matplotlib-fontja",
#   "pandas",
#   "numpy",
#   "seaborn",
# ]
# ///

import pickle
import tomllib
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib_fontja
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

def plot_median_history(df, category, genre_name, output_dir):
    print(f"Plotting Median History for {category}...")
    
    target_years = range(2011, 2026)
    median_history = []
    
    for year in target_years:
        data_year = df[df["year"] == year]["viewCounter"]
        median_history.append(np.median(data_year) if len(data_year) > 0 else 0)
    
    plt.figure(figsize=(14, 8))
    # Use a nice color from seaborn
    color = sns.color_palette("viridis", 1)[0]
    
    bars = plt.bar(target_years, median_history, color=color, alpha=0.85, edgecolor='white', linewidth=1.5)
    
    plt.ylim(0, max(median_history) * 1.2 if max(median_history) > 0 else 1000)
    plt.xlabel("年", fontsize=14)
    plt.ylabel("再生数中央値", fontsize=14)
    plt.title(f"{genre_name} 再生数中央値の推移 (2011-2025)", fontsize=18, fontweight='bold')
    
    # Add values on top of bars
    for i, v in enumerate(median_history):
        if v > 0:
            plt.text(target_years[i], v + (max(median_history) * 0.02), f"{int(v):,}", 
                     ha='center', fontsize=12, fontweight='bold', rotation=45)
    
    plt.xticks(target_years)
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    
    output_path = output_dir / f"{category}_median_history_2011_2025.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight", transparent=False)
    plt.close()
    print(f"Saved: {output_path}")

def main():
    with open("config.toml", "rb") as f:
        cfg = tomllib.load(f)
    
    for category in cfg.keys():
        df = preprocess(category)
        if df is None: continue
            
        genre_name = cfg[category]["title"].replace("ニコニコ ", "").replace(" 年次統計", "")
        
        output_dir = Path("results") / category
        output_dir.mkdir(parents=True, exist_ok=True)
        
        plot_median_history(df, category, genre_name, output_dir)

if __name__ == "__main__":
    main()
