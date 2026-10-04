# /// script
# dependencies = [
#   "pandas",
# ]
# ///
import pickle
import pandas as pd
from pathlib import Path
from common_utils import filter_software_talk

def count_whitecul_variants():
    pickle_path = Path("results/software_talk.pickle")
    if not pickle_path.exists():
        print("Pickle file not found.")
        return
        
    with open(pickle_path, "rb") as f:
        recv = pickle.load(f)
    df = pd.json_normalize(recv["data"])
    
    # ソフトウェアトーク以外の動画を除外
    df = filter_software_talk(df)
    
    # 2025年のデータに絞り込み
    df["startTime"] = pd.to_datetime(df["startTime"])
    df["year"] = df["startTime"].dt.year
    df_2025 = df[df["year"] == 2025]
    
    # 各動画のタグから "whitecul" を含むものを抽出（大文字小文字を区別してカウント）
    variant_counts = {}
    
    for _, row in df_2025.iterrows():
        tags = row.get("tags", "")
        if isinstance(tags, str):
            tag_list = tags.split()
        elif isinstance(tags, list):
            tag_list = tags
        else:
            tag_list = []
            
        # 1つの動画内で同じ表記が複数あっても1回と数える（動画単位のユニーク数）
        unique_variants_in_video = set()
        for tag in tag_list:
            if tag.lower() == "whitecul":
                unique_variants_in_video.add(tag)
            elif "whitecul" in tag.lower():
                # "WhiteCUL投稿祭" など、部分一致も含める場合はこちら
                # 今回は純粋な名前の表記ゆれを見たいので、完全一致を優先するが
                # ニコニコのタグ文化を考慮して、単語として含まれる場合も収集
                unique_variants_in_video.add(tag)
        
        for v in unique_variants_in_video:
            variant_counts[v] = variant_counts.get(v, 0) + 1
            
    # 投稿数順にソート
    sorted_variants = sorted(variant_counts.items(), key=lambda x: x[1], reverse=True)
    
    output_path = Path("results/whitecul_variants_2025.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# 2025年 WhiteCUL 表記ゆれ集計 (software_talk)\n\n")
        f.write("| タグ表記 | 投稿数 (ユニーク動画数) |\n")
        f.write("| :--- | :--- |\n")
        for variant, count in sorted_variants:
            f.write(f"| {variant} | {count} |\n")
            
    print(f"Results written to {output_path}")

if __name__ == "__main__":
    count_whitecul_variants()
