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
    
    # カラム名の大文字小文字を無視して探す
    col_map = {c.lower(): c for c in df.columns}
    if "lengthseconds" in col_map:
        target_col = col_map["lengthseconds"]
        df[target_col] = pd.to_numeric(df[target_col], errors='coerce')
        df = df.dropna(subset=[target_col])
    else:
        # デバッグ用
        # print(f"Columns in {category}: {df.columns.tolist()}")
        return None
        
    df["lengthSeconds"] = df[target_col]
    return df

def format_seconds(seconds):
    """秒を 分:秒 形式に変換"""
    if pd.isna(seconds): return "-"
    m, s = divmod(int(seconds), 60)
    return f"{m}:{s:02d}"

def main():
    with open("config.toml", "rb") as f:
        cfg = tomllib.load(f)
    
    target_years = [2018, 2021, 2025]
    all_results = []

    for category in cfg.keys():
        df = preprocess(category)
        if df is None: continue
            
        genre_name = cfg[category]["title"].replace("ニコニコ ", "").replace(" 年次統計", "")
        
        row = {"Genre": genre_name}
        for year in target_years:
            year_data = df[df["year"] == year]["lengthSeconds"]
            if len(year_data) == 0:
                row[year] = np.nan
            else:
                row[year] = np.median(year_data)
        
        all_results.append(row)

    result_df = pd.DataFrame(all_results)
    
    # 表示用にフォーマット
    display_df = result_df.copy()
    for year in target_years:
        display_df[year] = display_df[year].apply(format_seconds)
    
    md = "## ジャンル別 動画の長さ（再生時間）の中央値 推移\n\n"
    md += "数値は、その年に投稿された動画の長さの中央値（分:秒）です。\n\n"
    md += display_df.to_markdown(index=False)
    
    print(md)
    
    # ファイル保存
    output_path = Path("results/cdf_lorenz/video_length_stats.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md)

if __name__ == "__main__":
    main()
