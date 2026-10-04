import pickle
import pandas as pd
from pathlib import Path

def find_characters_precise(tags_list, character_names):
    if not isinstance(tags_list, list):
        return []
    tags_str = " ".join(tags_list)
    found = []
    for char in character_names:
        if char in tags_str:
            found.append(char)
    return found

def main():
    pickle_path = Path("results/onboard.pickle")
    with open(pickle_path, "rb") as f:
        recv = pickle.load(f)
    
    df = pd.json_normalize(recv["data"])
    df["startTime"] = pd.to_datetime(df["startTime"])
    df_2025 = df[df["startTime"].dt.year == 2025].copy()
    
    characters_df = pd.read_csv("characters.csv")
    character_names = characters_df["キャラクター名"].tolist()
    
    mapping_data = []
    for _, row in df_2025.iterrows():
        tags = row.get("tags", [])
        found = find_characters_precise(tags, character_names)
        for char in found:
            mapping_data.append({"character": char, "contentId": row["contentId"]})
            
    m_df = pd.DataFrame(mapping_data)
    counts = m_df.groupby("character")["contentId"].nunique().sort_values(ascending=False).reset_index()
    counts.columns = ["キャラクター", "投稿数"]
    counts["順位"] = range(1, len(counts) + 1)
    
    print("--- 2025年 車載ランキング Top 20 ---")
    print(counts.head(20).to_string(index=False))
    
    char_info = counts[counts["キャラクター"] == "すずきつづみ"]
    if not char_info.empty:
        print(f"\n【すずきつづみの順位】: {char_info.iloc[0]['順位']}位 ({char_info.iloc[0]['投稿数']}投稿)")

if __name__ == "__main__":
    main()
