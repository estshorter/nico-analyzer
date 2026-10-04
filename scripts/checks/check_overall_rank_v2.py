import pickle
import pandas as pd
from pathlib import Path
from common_utils import find_characters, filter_software_talk

def main():
    pickle_path = Path("results/software_talk.pickle")
    with open(pickle_path, "rb") as f:
        recv = pickle.load(f)
    
    df = pd.json_normalize(recv["data"])
    df = filter_software_talk(df)
    
    df["startTime"] = pd.to_datetime(df["startTime"])
    df_2025 = df[df["startTime"].dt.year == 2025].copy()
    
    characters_df = pd.read_csv("characters.csv")
    character_names = characters_df["キャラクター名"].tolist()
    
    # 高速化のためタグを文字列化してユニークなものにキャラ抽出
    df_2025["tags_str"] = df_2025["tags"].apply(lambda x: " ".join(x) if isinstance(x, list) else "")
    unique_tags = df_2025[["tags_str"]].drop_duplicates().copy()
    unique_tags["found"] = unique_tags["tags_str"].apply(lambda x: find_characters(x.split(), character_names))
    
    df_2025 = df_2025.merge(unique_tags, on="tags_str", how="left")
    
    mapping_data = []
    for _, row in df_2025.iterrows():
        for char in row["found"]:
            mapping_data.append({"character": char, "contentId": row["contentId"]})
            
    m_df = pd.DataFrame(mapping_data)
    counts = m_df.groupby("character")["contentId"].nunique().sort_values(ascending=False).reset_index()
    counts.columns = ["キャラクター", "投稿数"]
    counts["順位"] = range(1, len(counts) + 1)
    
    char_info = counts[counts["キャラクター"] == "すずきつづみ"]
    if not char_info.empty:
        rank = char_info.iloc[0]["順位"]
        count = char_info.iloc[0]["投稿数"]
        print(f"\n【すずきつづみの全体順位】: {rank}位 ({count}投稿)")
        
        # 20位〜30位を表示して周辺を確認
        print("\n--- 2025年 全体ランキング 20位-30位 ---")
        print(counts.iloc[19:30].to_markdown(index=False))
    else:
        print("\n【すずきつづみ】は見つかりませんでした。")

if __name__ == "__main__":
    main()
