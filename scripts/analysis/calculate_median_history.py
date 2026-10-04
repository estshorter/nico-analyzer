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

def main():
    with open("config.toml", "rb") as f:
        cfg = tomllib.load(f)
    
    target_years = [2018, 2022, 2025]
    all_results = []

    for category in cfg.keys():
        df = preprocess(category)
        if df is None: continue
            
        genre_name = cfg[category]["title"].replace("ニコニコ ", "").replace(" 年次統計", "")
        
        # 1. 各年の中央値
        medians = {}
        # 2. 2025年の1000再生の累積割合(Percentile)を取得
        data_2025 = df[df["year"] == 2025]["viewCounter"]
        if len(data_2025) == 0: continue
        
        # 1000再生以下の割合を計算
        pct_2025_1000 = (np.sum(data_2025 <= 1000) / len(data_2025)) * 100
        
        row = {"Genre": genre_name}
        
        for year in target_years:
            year_data = df[df["year"] == year]["viewCounter"]
            if len(year_data) == 0:
                row[f"{year} Median"] = "-"
                row[f"{year} EqVal"] = "-"
                continue
            
            # 中央値
            row[f"{year} Median"] = int(np.median(year_data))
            
            # 「2025年の1000再生と同じ立ち位置（累積割合）」が、その年では何再生だったか
            # percentile関数を使って、pct_2025_1000 に相当する再生数を逆引き
            eq_val = np.percentile(year_data, pct_2025_1000)
            row[f"{year} EqVal"] = int(eq_val)

        all_results.append(row)

    result_df = pd.DataFrame(all_results)
    
    # Markdownテーブル作成
    md = "## ジャンル別 再生数中央値と「1000再生」の歴史的価値\n\n"
    md += "「2025年の1000再生相当」列は、2025年における1000再生の立ち位置（例：下位70%）が、過去の年では何再生に相当したかを示します。\n\n"
    
    table_data = []
    for _, r in result_df.iterrows():
        table_data.append({
            "ジャンル": r["Genre"],
            "2018中央値": r["2018 Median"],
            "2022中央値": r["2022 Median"],
            "2025中央値": r["2025 Median"],
            "2018年の1000再生相当": f"{r['2018 EqVal']:,} 再生",
            "2022年の1000再生相当": f"{r['2022 EqVal']:,} 再生"
        })
    
    final_df = pd.DataFrame(table_data)
    print(final_df.to_markdown(index=False))
    
    # ファイル保存
    with open("results/cdf_lorenz/median_and_equity_stats.md", "w", encoding="utf-8") as f:
        f.write(md + final_df.to_markdown(index=False))

if __name__ == "__main__":
    main()
