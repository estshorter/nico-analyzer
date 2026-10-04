import pickle
import pandas as pd
import numpy as np
from pathlib import Path
from common_utils import filter_software_talk

GENRE_MAP = {
    "game": "ゲーム",
    "theater": "劇場",
    "explanation": "解説",
    "kitchen": "キッチン",
    "onboard": "車載",
    "travel": "旅行",
    "software_talk": "ボイロ全体"
}
GENRE_ORDER = ["game", "theater", "explanation", "kitchen", "onboard", "travel", "software_talk"]

def load_genre_data(genre_id):
    input_path = Path(f"results/{genre_id}.pickle")
    if not input_path.exists():
        return None

    with open(input_path, "rb") as f:
        raw_data = pickle.load(f)
    
    data = raw_data["data"] if isinstance(raw_data, dict) else raw_data
    df = pd.DataFrame(data)
    
    if genre_id == "software_talk":
        df = filter_software_talk(df)

    df["startTime"] = pd.to_datetime(df["startTime"])
    df = df[df["startTime"].dt.year == 2025].copy()
    
    if df.empty:
        return None

    df = df[df["viewCounter"] > 0].copy()
    return df

def export_thresholds():
    output_dir = Path("results/like_ratio")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "genre_view_thresholds.md"
    
    # より詳細な立ち位置を設定
    percentiles = [1, 3, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90]
    
    results = {}
    
    for genre_id in GENRE_ORDER:
        df = load_genre_data(genre_id)
        if df is None:
            continue
            
        thresholds = []
        for p in percentiles:
            q = 1 - (p / 100)
            val = df["viewCounter"].quantile(q)
            thresholds.append(int(val))
        
        results[GENRE_MAP[genre_id]] = thresholds

    # Create DataFrame for display
    threshold_df = pd.DataFrame(results, index=[f"上位 {p}%" for p in percentiles])
    threshold_df.index.name = "立ち位置"
    
    # Format as Markdown
    markdown_content = "# ジャンル別・立ち位置ごとの再生数しきい値 (2025年)\n\n"
    markdown_content += "各ジャンルにおいて、上位何％に入るために必要な再生数の目安です。\n\n"
    markdown_content += threshold_df.to_markdown()
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    
    print(f"Exported thresholds to {output_path}")

if __name__ == "__main__":
    export_thresholds()
