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
    
    # userIdが欠損している場合は0埋め（通常は存在すべきだが念のため）
    if "userId" in df.columns:
        df["userId"] = df["userId"].fillna(0).astype("uint64")
    else:
        df["userId"] = 0
    return df

def calculate_gini(values):
    if len(values) == 0:
        return np.nan
    sorted_values = np.sort(values)
    n = len(values)
    index = np.arange(1, n + 1)
    return (2 * np.sum(index * sorted_values) / (n * np.sum(sorted_values))) - (n + 1) / n

def main():
    with open("config.toml", "rb") as f:
        cfg = tomllib.load(f)
    
    target_years = [2018, 2021, 2025]
    all_results = []

    for category in cfg.keys():
        df = preprocess(category)
        if df is None:
            continue
            
        genre_name = cfg[category]["title"].replace("ニコニコ ", "").replace(" 年次統計", "")
        
        for year in target_years:
            year_data = df[df["year"] == year]
            if len(year_data) == 0:
                continue
            
            # 1. 動画別のGini係数 (Video Gini)
            video_gini = calculate_gini(year_data["viewCounter"].values)
            
            # 2. ユーザー別のGini係数 (User Gini)
            # userIdごとにその年のviewCounterを合計する
            user_views = year_data.groupby("userId")["viewCounter"].sum().values
            user_gini = calculate_gini(user_views)
            
            all_results.append({
                "Genre": genre_name,
                "Year": year,
                "Unique Users": len(user_views),
                "Video-Gini": video_gini,
                "User-Gini": user_gini,
                "Diff": user_gini - video_gini
            })

    result_df = pd.DataFrame(all_results)
    
    # 見やすくピボットした比較表
    md_content = "## 動画別 vs ユーザー別 ジニ係数 比較\n\n"
    
    # User-Gini のピボット
    pivot_user = result_df.pivot(index="Genre", columns="Year", values="User-Gini")
    md_content += "### ユーザー別（投稿者別）ジニ係数（界隈の寡占度）\n"
    md_content += pivot_user.round(3).to_markdown() + "\n\n"
    
    # Video-Gini のピボット
    pivot_video = result_df.pivot(index="Genre", columns="Year", values="Video-Gini")
    md_content += "### （参考）動画別ジニ係数\n"
    md_content += pivot_video.round(3).to_markdown() + "\n\n"

    print(md_content)
    
    # ファイル保存
    output_path = Path("results/cdf_lorenz/user_gini_stats.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md_content)

if __name__ == "__main__":
    main()
