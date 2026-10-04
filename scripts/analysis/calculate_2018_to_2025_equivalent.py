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
    
    # 2018年の1000再生が、各年でどの程度の立ち位置（上位何%）に相当したか
    # そしてその立ち位置が2025年では何再生に相当するかを算出する
    
    target_year_base = 2018
    target_year_current = 2025
    reference_view = 1000
    
    all_results = []

    for category in cfg.keys():
        df = preprocess(category)
        if df is None: continue
            
        genre_name = cfg[category]["title"].replace("ニコニコ ", "").replace(" 年次統計", "")
        
        data_2018 = df[df["year"] == 2018]["viewCounter"]
        data_2022 = df[df["year"] == 2022]["viewCounter"]
        data_2025 = df[df["year"] == 2025]["viewCounter"]
        
        if len(data_2018) == 0 or len(data_2025) == 0:
            continue
            
        # 1. 2018年における1000再生の累積割合(Percentile)を取得
        pct_2018_1000 = (np.sum(data_2018 <= reference_view) / len(data_2018)) * 100
        rank_2018 = 100 - pct_2018_1000
        
        # 2. その累積割合が2022年、2025年では何再生に相当するか
        eq_val_2022 = np.percentile(data_2022, pct_2018_1000) if len(data_2022) > 0 else np.nan
        eq_val_2025 = np.percentile(data_2025, pct_2018_1000)
        
        # 3. 逆：2025年の1000再生が2018年では何再生だったか（おまけ）
        pct_2025_1000 = (np.sum(data_2025 <= reference_view) / len(data_2025)) * 100
        eq_val_2018_from_2025 = np.percentile(data_2018, pct_2025_1000)

        all_results.append({
            "ジャンル": genre_name,
            "2018年1000再生の順位": f"上位 {rank_2018:.1f}%",
            "2018年中央値": int(np.median(data_2018)),
            "2025年中央値": int(np.median(data_2025)),
            "2018年1000再生 ≒ 2022年": f"{int(eq_val_2022):,} 再生" if not np.isnan(eq_val_2022) else "-",
            "2018年1000再生 ≒ 2025年": f"{int(eq_val_2025):,} 再生",
            "備考": f"2025年の1000再生は2018年の {int(eq_val_2018_from_2025):,} 再生相当"
        })

    result_df = pd.DataFrame(all_results)
    
    # Markdownテーブル作成
    md = f"## 2018年の1000再生は、2025年で何再生に相当するか？\n\n"
    md += f"2018年当時の「1000再生」という壁が、各ジャンルの全動画の中でどの程度の相対的順位（上位何％）に位置していたかを算出し、"
    md += f"同じ相対的順位を2025年の分布に当てはめた場合の再生数を計算しました。\n\n"
    
    print(result_df.to_markdown(index=False))
    
    # ファイル保存
    output_path = Path("results/cdf_lorenz/equivalent_1000_stats.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md + result_df.to_markdown(index=False))

if __name__ == "__main__":
    main()
