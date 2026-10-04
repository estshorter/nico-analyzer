import pickle
import pandas as pd
from pathlib import Path
from common_utils import filter_software_talk

def find_characters_precise(tags_list, character_names):
    if not isinstance(tags_list, list):
        return []
    tags_str = " ".join(tags_list)
    found = []
    for char in character_names:
        if char in tags_str:
            found.append(char)
    return found

def get_full_ranking_2025(category_name, character_name="すずきつづみ"):
    pickle_path = Path(f"results/{category_name}.pickle")
    if not pickle_path.exists():
        print(f"Error: {pickle_path} not found")
        return None

    with open(pickle_path, "rb") as f:
        recv = pickle.load(f)
    
    df = pd.json_normalize(recv["data"])
    
    # ソフトウェアトーク全体の場合はフィルタ適用
    if category_name == "software_talk":
        df = filter_software_talk(df)
    
    df["startTime"] = pd.to_datetime(df["startTime"])
    df_2025 = df[df["startTime"].dt.year == 2025].copy()
    
    characters_df = pd.read_csv("characters.csv")
    character_names = characters_df["キャラクター名"].tolist()
    
    mapping_data = []
    for _, row in df_2025.iterrows():
        # tagsがリスト形式であることを期待
        tags = row.get("tags", [])
        found = find_characters_precise(tags, character_names)
        for char in found:
            mapping_data.append({"character": char, "contentId": row["contentId"]})
            
    if not mapping_data:
        return None
        
    m_df = pd.DataFrame(mapping_data)
    counts = m_df.groupby("character")["contentId"].nunique().sort_values(ascending=False).reset_index()
    counts.columns = ["キャラクター", "投稿数"]
    counts["順位"] = range(1, len(counts) + 1)
    
    char_info = counts[counts["キャラクター"] == character_name]
    if not char_info.empty:
        return {
            "rank": char_info.iloc[0]["順位"],
            "posts": char_info.iloc[0]["投稿数"],
            "total_characters": len(counts)
        }
    else:
        return None

def main():
    char_name = "すずきつづみ"
    print(f"--- {char_name} の2025年最新集計 (Pickle直読) ---")
    
    # 全体 (software_talk)
    overall = get_full_ranking_2025("software_talk", char_name)
    if overall:
        print(f"【全体】: {overall['rank']}位 / {overall['total_characters']}キャラ中 ({overall['posts']}投稿)")
    
    # 車載 (onboard)
    onboard = get_full_ranking_2025("onboard", char_name)
    if onboard:
        print(f"【車載】: {onboard['rank']}位 / {onboard['total_characters']}キャラ中 ({onboard['posts']}投稿)")

if __name__ == "__main__":
    main()
