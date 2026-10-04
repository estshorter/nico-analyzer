# /// script
# dependencies = [
#   "pandas",
#   "numpy",
# ]
# ///

import pandas as pd
import pickle
from pathlib import Path
from common_utils import filter_software_talk

GENRE_MAP = {
    'game': 'ゲーム',
    'theater': '劇場',
    'explanation': '解説',
    'kitchen': 'キッチン',
    'onboard': '車載',
    'travel': '旅行',
    'software_talk': 'ボイロ全体'
}
GENRE_ORDER = ['game', 'theater', 'explanation', 'kitchen', 'onboard', 'travel', 'software_talk']

def export_stats():
    output_dir = Path("results/like_ratio")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "median_stats_500_1000.md"
    
    rows = []
    for genre_id in GENRE_ORDER:
        input_path = Path(f'results/{genre_id}.pickle')
        if not input_path.exists(): continue
        
        with open(input_path, 'rb') as f:
            raw_data = pickle.load(f)
        data = raw_data['data'] if isinstance(raw_data, dict) else raw_data
        df = pd.DataFrame(data)
        if genre_id == 'software_talk': df = filter_software_talk(df)
        
        df['startTime'] = pd.to_datetime(df['startTime'])
        df = df[df['startTime'].dt.year == 2025].copy()
        
        # 500〜1000再生に絞る
        df_filtered = df[(df['viewCounter'] >= 500) & (df['viewCounter'] < 1000)].copy()
        
        if df_filtered.empty:
            rows.append([GENRE_MAP[genre_id], "0", "-"])
            continue
            
        df_filtered['likeRatio'] = df_filtered['likeCounter'] / df_filtered['viewCounter']
        median_val = df_filtered['likeRatio'].median()
        count = len(df_filtered)
        
        rows.append([GENRE_MAP[genre_id], f"{count:,}", f"{median_val*100:.2f}%"])

    # Markdownテーブル作成
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# 500-1000再生層 ジャンル別いいね率中央値 (2025年)\n\n")
        f.write("| ジャンル | 動画本数 | いいね率中央値 |\n")
        f.write("| :--- | :---: | :---: |\n")
        for row in rows:
            f.write(f"| {' | '.join(row)} |\n")
            
    print(f"Stats exported to: {output_path}")

if __name__ == "__main__":
    export_stats()
