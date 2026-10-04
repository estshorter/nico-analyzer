# /// script
# dependencies = [
#   "pandas",
# ]
# ///
import pickle
import pandas as pd
from pathlib import Path
from common_utils import filter_software_talk, find_characters

def main():
    pickle_path = Path("results/software_talk.pickle")
    if not pickle_path.exists():
        print(f"Error: {pickle_path} not found.")
        return
        
    print(f"Loading {pickle_path}...")
    with open(pickle_path, "rb") as f:
        recv = pickle.load(f)
    
    df = pd.json_normalize(recv["data"])
    
    # Filter software_talk
    df = filter_software_talk(df)
    
    # Filter for 2025
    df["startTime"] = pd.to_datetime(df["startTime"])
    df["year"] = df["startTime"].dt.year
    df_2025 = df[df["year"] == 2025].copy()
    
    # Filter for "ヤンデレ" in title or tags
    df_2025["tags_str"] = df_2025["tags"].apply(lambda x: " ".join(x) if isinstance(x, list) else str(x))
    yandere_mask = df_2025["title"].str.contains("ヤンデレ", case=False, na=False) | \
                   df_2025["tags_str"].str.contains("ヤンデレ", case=False, na=False)
    df_yandere = df_2025[yandere_mask].copy()
    
    # Load character names
    characters_df = pd.read_csv("characters.csv")
    character_names = characters_df["キャラクター名"].tolist()
    
    # Extract characters
    df_yandere["found_characters"] = df_yandere["tags"].apply(lambda x: find_characters(x, character_names))
    
    # Identify Top 10 Characters (from previous ranking, excluding "不明/その他")
    # To be precise, we re-calculate from this dataframe
    mapping_data = []
    for _, row in df_yandere.iterrows():
        for char in row["found_characters"]:
            mapping_data.append({"character": char, "contentId": row["contentId"]})
    
    m_df = pd.DataFrame(mapping_data)
    char_counts = m_df.groupby("character")["contentId"].nunique().sort_values(ascending=False).head(11)
    top_chars = [c for c in char_counts.index if c != "不明/その他"][:10]
    
    output_path = "results/yandere_top_videos_by_character.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# 2025年 ヤンデレ動画 キャラクター別再生数ランキング (TOP 10)\n\n")
        f.write("各キャラクター（投稿数上位10名）について、再生数の多い順に最大10件の動画を表示します。\n\n")
        
        for char in top_chars:
            f.write(f"## {char}\n\n")
            # Filter videos containing this character
            char_videos = df_yandere[df_yandere["found_characters"].apply(lambda x: char in x)].copy()
            # Sort by viewCounter
            char_videos = char_videos.sort_values("viewCounter", ascending=False).head(10)
            
            if char_videos.empty:
                f.write("該当する動画がありません。\n\n")
                continue
                
            f.write("| 順位 | タイトル | 再生数 | 投稿日 | URL |\n")
            f.write("| :--- | :--- | :--- | :--- | :--- |\n")
            
            for i, (_, row) in enumerate(char_videos.iterrows(), 1):
                title = row["title"].replace("|", "｜") # Escape pipe
                view_count = f"{row['viewCounter']:,}"
                date = row["startTime"].strftime("%Y/%m/%d")
                url = f"https://www.nicovideo.jp/watch/{row['contentId']}"
                f.write(f"| {i} | {title} | {view_count} | {date} | [リンク]({url}) |\n")
            
            f.write("\n")
            
    print(f"Results saved to {output_path}")

if __name__ == "__main__":
    main()
