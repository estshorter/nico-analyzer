# /// script
# dependencies = [
#   "pandas",
# ]
# ///

import pickle
import pandas as pd
from pathlib import Path
from common_utils import filter_software_talk, find_characters

def get_stats():
    target_characters = [
        "結月ゆかり", "琴葉茜", "紲星あかり", "東北きりたん", "ずんだもん",
        "琴葉葵", "春日部つむぎ", "弦巻マキ", "東北ずん子", "東北イタコ", "宮舞モカ"
    ]
    
    categories = ["software_talk", "game", "onboard", "kitchen", "explanation", "theater", "travel", "fishing"]
    category_labels = {
        "software_talk": "全体",
        "game": "実況",
        "onboard": "車載",
        "kitchen": "キッチン",
        "explanation": "解説",
        "theater": "劇場",
        "travel": "旅行",
        "fishing": "釣り",
    }

    characters_df = pd.read_csv("characters.csv")
    character_names = characters_df["キャラクター名"].tolist()

    results = {char: {"2025_views": 0, "2025_overall_rank": "-", "total_views": 0, "total_overall_rank": "-", "ranks": {}} for char in target_characters}
    
    # Store overall 2025 rankings to find who is 11th
    top_2025_global = None

    for cat in categories:
        pickle_path = Path(f"results/{cat}.pickle")
        if not pickle_path.exists():
            continue
            
        with open(pickle_path, "rb") as f:
            recv = pickle.load(f)
        df = pd.json_normalize(recv["data"])
        
        if cat == "software_talk":
            df = filter_software_talk(df)
            
        df["startTime"] = pd.to_datetime(df["startTime"])
        df["year"] = df["startTime"].dt.year
        df["viewCounter"] = df["viewCounter"].astype(int)
        
        # Only up to 2025
        df = df[df["year"] <= 2025]
        
        df["found_characters"] = df["tags"].apply(lambda x: find_characters(x, character_names))
        
        # Explode to get mapping
        mapping_data = []
        for _, row in df.iterrows():
            for char in row["found_characters"]:
                mapping_data.append({
                    "character": char,
                    "viewCounter": row["viewCounter"],
                    "year": row["year"]
                })
        
        if not mapping_data:
            continue
            
        m_df = pd.DataFrame(mapping_data)
        
        # 2025年のデータのみで順位を計算
        m_df_2025 = m_df[m_df["year"] == 2025]
        views_2025 = m_df_2025.groupby("character")["viewCounter"].sum().sort_values(ascending=False)
        rankings_2025 = views_2025.rank(ascending=False, method="min").astype(int)
        
        if cat == "software_talk":
            top_2025_global = views_2025

        # 通年（〜2025）の順位を計算
        overall_views = m_df.groupby("character")["viewCounter"].sum().sort_values(ascending=False)
        overall_rankings = overall_views.rank(ascending=False, method="min").astype(int)

        # Specific stats for target characters
        for char in target_characters:
            if cat == "software_talk":
                # 全体累計再生数と順位
                if char in overall_views.index:
                    results[char]["total_views"] = int(overall_views[char])
                    results[char]["total_overall_rank"] = int(overall_rankings[char])
                
                # 2025年累計再生数と順位
                if char in views_2025.index:
                    results[char]["2025_views"] = int(views_2025[char])
                    results[char]["2025_overall_rank"] = int(rankings_2025[char])
            
            # 2025年のジャンル別順位を記録
            if char in rankings_2025.index:
                results[char]["ranks"][category_labels[cat]] = rankings_2025[char]
            else:
                results[char]["ranks"][category_labels[cat]] = "-"

    # Debug: Print top 15 of 2025
    if top_2025_global is not None:
        print("\n--- 2025年 総合順位 TOP 15 ---")
        for i, (name, views) in enumerate(top_2025_global.head(15).items(), 1):
            print(f"{i}位: {name} ({views:,}回)")
        print("------------------------------\n")

    # Output results as Markdown
    header = "| キャラクター | 2025年再生数 | 2025年総合順位 | 通年再生数 | 通年総合順位 | 各ジャンルでの順位 (高い方から) |"
    separator = "|---|---|---|---|---|---|"
    lines = [
        "# キャラクター別統計レポート (2025年ベース)",
        "",
        "このレポートは、`software_talk.pickle` を含む各ジャンルのデータを元に、主要キャラクターの再生数と2025年のジャンル別順位をまとめたものです。",
        "",
        header,
        separator
    ]

    for char in target_characters:
        stats = results[char]
        sorted_ranks = sorted(
            [(k, v) for k, v in stats["ranks"].items() if v != "-"],
            key=lambda x: x[1]
        )
        ranks_str = ", ".join([f"{k}:{v}位" for k, v in sorted_ranks])
        line = f"| **{char}** | {stats['2025_views']:,} | {stats['2025_overall_rank']}位 | {stats['total_views']:,} | {stats['total_overall_rank']}位 | {ranks_str} |"
        lines.append(line)
    
    lines.append("")
    lines.append("---")
    lines.append("※再生数は2025年12月31日までの集計値です。")
    lines.append("※「総合順位」は全キャラクター中での再生数順位です。")

    output_content = "\n".join(lines)
    print("\n" + output_content)

    with open("results/character_stats_2025.md", "w", encoding="utf-8") as f:
        f.write(output_content)
    print(f"\nReport saved to results/character_stats_2025.md")

if __name__ == "__main__":
    get_stats()
