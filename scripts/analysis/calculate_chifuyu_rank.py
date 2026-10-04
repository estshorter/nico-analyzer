import pickle
import pandas as pd
from pathlib import Path
import json

# 共通ユーティリティのロジックをインライン化して確実に動作させる
def find_characters(tags_str, character_names):
    if not isinstance(tags_str, str):
        return []
    found = []
    for char in character_names:
        if char in tags_str:
            found.append(char)
    return found

def calculate_full_ranking_2025():
    pickle_path = Path("results/software_talk.pickle")
    if not pickle_path.exists():
        print("Error: software_talk.pickle not found")
        return

    print("Loading data...")
    with open(pickle_path, "rb") as f:
        recv = pickle.load(f)
    
    df = pd.json_normalize(recv["data"])
    
    print("Filtering 2025 data...")
    df["startTime"] = pd.to_datetime(df["startTime"])
    df_2025 = df[df["startTime"].dt.year == 2025]
    
    characters_df = pd.read_csv("characters.csv")
    character_names = characters_df["キャラクター名"].tolist()
    
    print("Extracting characters from tags...")
    mapping_data = []
    for _, row in df_2025.iterrows():
        tags = row.get("tags", "")
        found = find_characters(tags, character_names)
        for char in found:
            mapping_data.append({"character": char, "contentId": row["contentId"]})
            
    if not mapping_data:
        print("No characters found.")
        return
        
    m_df = pd.DataFrame(mapping_data)
    counts = m_df.groupby("character")["contentId"].nunique().sort_values(ascending=False).reset_index()
    counts.columns = ["キャラクター", "投稿数"]
    counts["順位"] = range(1, len(counts) + 1)
    
    print("\n--- 2025年 全体投稿数ランキング (詳細) ---")
    print(counts.head(30).to_string(index=False))
    
    chifuyu_info = counts[counts["キャラクター"] == "花隈千冬"]
    if not chifuyu_info.empty:
        rank = chifuyu_info.iloc[0]["順位"]
        count = chifuyu_info.iloc[0]["投稿数"]
        print(f"\n【花隈千冬の順位】: {rank}位 ({count}投稿)")
    else:
        print("\n【花隈千冬の順位】: データ内に見つかりませんでした。")

if __name__ == "__main__":
    calculate_full_ranking_2025()
