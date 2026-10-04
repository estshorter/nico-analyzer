import pickle
import pandas as pd
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
    df["likeRatio"] = df["likeCounter"] / df["viewCounter"]
    return df

def export_thresholds():
    output_dir = Path("results/like_ratio")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    percentiles = [1, 3, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90]
    
    results_ratio = {}
    results_count = {}
    
    for genre_id in GENRE_ORDER:
        df = load_genre_data(genre_id)
        if df is None:
            continue
            
        thresholds_ratio = []
        thresholds_count = []
        for p in percentiles:
            q = 1 - (p / 100)
            # like ratio
            val_r = df["likeRatio"].quantile(q)
            thresholds_ratio.append(f"{val_r * 100:.2f}%")
            # like count
            val_c = df["likeCounter"].quantile(q)
            thresholds_count.append(int(val_c))
        
        results_ratio[GENRE_MAP[genre_id]] = thresholds_ratio
        results_count[GENRE_MAP[genre_id]] = thresholds_count

    # Create DataFrames
    df_ratio = pd.DataFrame(results_ratio, index=[f"上位 {p}%" for p in percentiles])
    df_ratio.index.name = "立ち位置"
    
    df_count = pd.DataFrame(results_count, index=[f"上位 {p}%" for p in percentiles])
    df_count.index.name = "立ち位置"
    
    # Format as Markdown
    md_ratio = "# ジャンル別・立ち位置ごとのいいね率しきい値 (2025年)\n\n"
    md_ratio += "各ジャンルにおいて、上位何％に入るために必要ないいね率の目安です。\n\n"
    md_ratio += df_ratio.to_markdown()
    
    md_count = "# ジャンル別・立ち位置ごとのいいね数しきい値 (2025年)\n\n"
    md_count += "各ジャンルにおいて、上位何％に入るために必要ないいね数の目安です。\n\n"
    md_count += df_count.to_markdown()
    
    with open(output_dir / "genre_like_ratio_thresholds.md", "w", encoding="utf-8") as f:
        f.write(md_ratio)
        
    with open(output_dir / "genre_like_count_thresholds.md", "w", encoding="utf-8") as f:
        f.write(md_count)
    
    print("Done generating thresholds.")

if __name__ == "__main__":
    export_thresholds()
