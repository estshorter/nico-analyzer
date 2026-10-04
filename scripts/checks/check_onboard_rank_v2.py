import pickle
import pandas as pd
from pathlib import Path
from common_utils import find_characters

def main():
    pickle_path = Path("results/onboard.pickle")
    if not pickle_path.exists():
        print(f"Error: {pickle_path} not found")
        return

    with open(pickle_path, "rb") as f:
        recv = pickle.load(f)
    
    df = pd.json_normalize(recv["data"])
    df["startTime"] = pd.to_datetime(df["startTime"])
    df_2025 = df[df["startTime"].dt.year == 2025].copy()
    
    print(f"Total videos in 2025 (onboard): {len(df_2025)}")
    
    characters_df = pd.read_csv("characters.csv")
    character_names = characters_df["キャラクター名"].tolist()
    
    mapping_data = []
    for _, row in df_2025.iterrows():
        tags = row.get("tags", [])
        found = find_characters(tags, character_names)
        for char in found:
            mapping_data.append({"character": char, "contentId": row["contentId"]})
            
    if not mapping_data:
        print("No characters found in mapping.")
        return
        
    m_df = pd.DataFrame(mapping_data)
    counts = m_df.groupby("character")["contentId"].nunique().sort_values(ascending=False).reset_index()
    counts.columns = ["キャラクター", "投稿数"]
    counts["順位"] = range(1, len(counts) + 1)
    
    print("\n--- 2025年 車載ランキング Top 30 ---")
    print(counts.head(30).to_markdown(index=False))
    
    char_info = counts[counts["キャラクター"] == "すずきつづみ"]
    if not char_info.empty:
        rank = char_info.iloc[0]["順位"]
        count = char_info.iloc[0]["投稿数"]
        print(f"\n【すずきつづみの順位】: {rank}位 ({count}投稿)")
    else:
        print("\n【すずきつづみ】は見つかりませんでした。")

if __name__ == "__main__":
    main()
