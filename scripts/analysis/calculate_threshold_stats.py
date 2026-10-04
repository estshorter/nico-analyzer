# /// script
# dependencies = [
#   "pandas",
#   "numpy",
#   "tabulate",
# ]
# ///

import pickle
import tomllib
from pathlib import Path
import pandas as pd
import numpy as np

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

def calculate_cdf_at_thresholds(views, thresholds=[1000, 5000, 10000]):
    if len(views) == 0:
        return {t: np.nan for t in thresholds}
    
    n = len(views)
    results = {}
    for t in thresholds:
        # threshold以下の動画の数をカウント
        count = np.sum(views <= t)
        results[t] = (count / n) * 100
    return results

def main():
    with open("config.toml", "rb") as f:
        cfg = tomllib.load(f)
    
    target_years = [2018, 2022, 2025]
    thresholds = [1000, 5000, 10000]
    
    all_results = []

    for category in cfg.keys():
        df = preprocess(category)
        if df is None:
            continue
            
        genre_name = cfg[category]["title"].replace("ニコニコ ", "").replace(" 年次統計", "")
        
        for year in target_years:
            year_data = df[df["year"] == year]["viewCounter"]
            if len(year_data) == 0:
                continue
            
            stats = calculate_cdf_at_thresholds(year_data.values, thresholds)
            res = {
                "Genre": genre_name,
                "Year": year,
                "Total Videos": len(year_data)
            }
            for t in thresholds:
                res[f"≤{t} views (%)"] = f"{stats[t]:.1f}%"
            
            all_results.append(res)

    result_df = pd.DataFrame(all_results)
    
    # 比較しやすいようにピボット表示用なども含め、Markdownとして出力
    md_output = "## 再生数しきい値別 累積割合 (CDF) 詳細\n\n"
    md_output += "数値（%）は、その再生数**以下**の動画が占める割合を示します。\n\n"
    md_output += result_df.to_markdown(index=False)
    
    print(md_output)
    
    # ファイルにも保存
    output_path = Path("results/cdf_lorenz/view_threshold_stats.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md_output)

if __name__ == "__main__":
    main()
