# /// script
# dependencies = [
#   "matplotlib",
#   "matplotlib-fontja",
#   "pandas",
#   "seaborn",
#   "numpy",
#   "tabulate",
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
    # フォント設定
    plt.rcParams['font.family'] = ['IBM Plex Sans JP', 'BIZ UDGothic', 'Yu Gothic', 'Meiryo', 'MS Gothic', 'sans-serif']
    plt.rcParams['font.weight'] = 'bold'
    plt.rcParams['font.size'] = 16
    plt.rcParams['axes.titlesize'] = 24
    plt.rcParams['axes.labelsize'] = 20
    plt.rcParams['axes.labelweight'] = 'bold'
    plt.rcParams['axes.titleweight'] = 'bold'
    plt.rcParams['legend.fontsize'] = 12
    plt.rcParams['xtick.labelsize'] = 16
    plt.rcParams['ytick.labelsize'] = 16
    plt.rcParams['figure.dpi'] = 200

    log_formatter = ticker.FuncFormatter(lambda x, pos: f'{int(x):,}' if x >= 1 else f'{x}')
    
    # 年ごとの色を定義
    year_colors = {
        2025: "#e41a1c", # 赤
        2024: "#377eb8", # 青
        2023: "#4daf4a", # 緑
        2022: "#984ea3", # 紫
        2019: "#ff7f00", # オレンジ
    }
    
    grid_style_base = {
        'color': '#b0b0b0', 
        'alpha': 0.7,
        'linewidth': 1.0
    }
    
    threshold_style = {
        **grid_style_base,
        'linestyle': '--'
    }
    
    df_onboard = preprocess("onboard")
    if df_onboard is None:
        print("Error: onboard.pickle not found.")
        return

    # 比較対象の定義
    comparison_configs = [
        {"year": 2025, "gw_start": "2025-04-26", "gw_end": "2025-05-06"},
        {"year": 2024, "gw_start": "2024-04-27", "gw_end": "2024-05-06"},
        {"year": 2023, "gw_start": "2023-04-29", "gw_end": "2023-05-07"},
        {"year": 2022, "gw_start": "2022-04-29", "gw_end": "2022-05-08"},
        {"year": 2019, "gw_start": "2019-04-27", "gw_end": "2019-05-06"},
    ]

    plt.figure(figsize=(14, 10))
    
    stats = []

    for config in comparison_configs:
        year = config["year"]
        color = year_colors[year]
        
        # 通年データ
        data_annual = df_onboard[df_onboard["year"] == year]["viewCounter"]
        if len(data_annual) > 0:
            median_annual = np.median(data_annual)
            stats.append({"期間": f"{year}年 通年", "中央値": median_annual, "動画数": len(data_annual)})
            
            sorted_views = np.sort(data_annual.values)
            cdf = np.arange(1, len(sorted_views) + 1) / len(sorted_views)
            plt.plot(np.maximum(sorted_views, 1), cdf * 100, color=color, linewidth=2, linestyle="--", alpha=0.6, label=f"{year}年 通年")

        # GWデータ
        start_dt = pd.Timestamp(config["gw_start"] + " 00:00:00").tz_localize("Asia/Tokyo")
        end_dt = pd.Timestamp(config["gw_end"] + " 23:59:59").tz_localize("Asia/Tokyo")
        mask = (df_onboard["startTime"] >= start_dt) & (df_onboard["startTime"] <= end_dt)
        data_gw = df_onboard[mask]["viewCounter"]
        
        if len(data_gw) > 0:
            median_gw = np.median(data_gw)
            stats.append({"期間": f"{year}年 GW", "中央値": median_gw, "動画数": len(data_gw)})
            
            sorted_views = np.sort(data_gw.values)
            cdf = np.arange(1, len(sorted_views) + 1) / len(sorted_views)
            plt.plot(np.maximum(sorted_views, 1), cdf * 100, color=color, linewidth=4, linestyle="-", alpha=1.0, label=f"{year}年 GW")

    # 表示順を整理するために統計情報を表示
    print(pd.DataFrame(stats).to_string(index=False))

    plt.xscale("log")
    plt.gca().xaxis.set_major_formatter(log_formatter)
    plt.xlim(100, 10000)
    plt.xlabel("再生数 (対数軸)")
    plt.ylabel("累積割合 (%)")
    plt.title("ボイロ車載動画 年次別GW vs 通年 再生数累積分布")
    
    plt.axhline(50, **threshold_style)
    plt.axhline(70, **threshold_style)
    
    plt.grid(True, which="major", axis="y", linestyle='-', color=grid_style_base['color'], alpha=grid_style_base['alpha'], linewidth=grid_style_base['linewidth'])
    plt.grid(True, which="both", axis="x", linestyle="--", alpha=0.4)
    
    plt.legend(loc='upper left', frameon=True, shadow=False, ncol=2)
    
    output_path = "results/onboard/onboard_view_cdf_gw_vs_annual.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight", transparent=False)
    print(f"Saved: {output_path}")
    plt.close()

if __name__ == "__main__":
    main()
