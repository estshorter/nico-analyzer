import pandas as pd
from pathlib import Path

def get_character_rank_2025(category_name, character_name="すずきつづみ"):
    cache_path = Path(f"results/history/cache/{category_name}_processed_v2.csv")
    if not cache_path.exists():
        print(f"Error: {cache_path} not found")
        return None

    df = pd.read_csv(cache_path)
    df_2025 = df[df["year"] == 2025]
    
    # character列でカウント
    counts = df_2025.groupby("character")["contentId"].nunique().sort_values(ascending=False).reset_index()
    counts.columns = ["character", "posts"]
    counts["rank"] = range(1, len(counts) + 1)
    
    char_info = counts[counts["character"] == character_name]
    if not char_info.empty:
        return {
            "rank": char_info.iloc[0]["rank"],
            "posts": char_info.iloc[0]["posts"],
            "total_characters": len(counts)
        }
    else:
        return None

def main():
    char_name = "すずきつづみ"
    
    print(f"--- {char_name} の2025年ランキング集計 ---")
    
    # 全体 (software_talk)
    overall_info = get_character_rank_2025("software_talk", char_name)
    if overall_info:
        print(f"【全体】: {overall_info['rank']}位 / {overall_info['total_characters']}キャラ中 ({overall_info['posts']}投稿)")
    else:
        print(f"【全体】: データが見つかりませんでした")
        
    # 車載 (onboard)
    onboard_info = get_character_rank_2025("onboard", char_name)
    if onboard_info:
        print(f"【車載】: {onboard_info['rank']}位 / {onboard_info['total_characters']}キャラ中 ({onboard_info['posts']}投稿)")
    else:
        print(f"【車載】: データが見つかりませんでした")

if __name__ == "__main__":
    main()
