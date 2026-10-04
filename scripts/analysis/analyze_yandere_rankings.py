# /// script
# dependencies = [
#   "pandas",
#   "tabulate",
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
    print(f"Total videos: {len(df)}")
    
    # Filter software_talk (remove music/VOCALOID)
    df = filter_software_talk(df)
    
    # Filter for 2025
    df["startTime"] = pd.to_datetime(df["startTime"])
    df["year"] = df["startTime"].dt.year
    df = df[df["year"] == 2025].copy()
    print(f"Videos in 2025: {len(df)}")
    
    # Filter for "ヤンデレ" in title or tags
    # Ensure tags are string for searching
    df["tags_str"] = df["tags"].apply(lambda x: " ".join(x) if isinstance(x, list) else str(x))
    
    yandere_mask = df["title"].str.contains("ヤンデレ", case=False, na=False) | \
                   df["tags_str"].str.contains("ヤンデレ", case=False, na=False)
    
    df_yandere = df[yandere_mask].copy()
    print(f"Yandere-related videos: {len(df_yandere)}")
    
    if df_yandere.empty:
        print("No Yandere-related videos found.")
        return
        
    # Load character names
    characters_df = pd.read_csv("characters.csv")
    character_names = characters_df["キャラクター名"].tolist()
    
    # Extract characters
    print("Extracting characters from tags...")
    df_yandere["found_characters"] = df_yandere["tags"].apply(lambda x: find_characters(x, character_names))
    
    mapping_data = []
    for _, row in df_yandere.iterrows():
        if not row["found_characters"]:
            # If no character found in tags, maybe try title? 
            # But the requirement usually follows common_utils.find_characters which looks at tags.
            # Let's stick to tags first as per generate_2025_rankings_table.py
            mapping_data.append({"character": "不明/その他", "contentId": row["contentId"]})
        else:
            for char in row["found_characters"]:
                mapping_data.append({"character": char, "contentId": row["contentId"]})
            
    m_df = pd.DataFrame(mapping_data)
    counts = m_df.groupby("character")["contentId"].nunique().sort_values(ascending=False).reset_index()
    counts.columns = ["キャラクター", "投稿数"]
    
    # Calculate percentage
    total_yandere_videos = df_yandere["contentId"].nunique()
    counts["比率(%)"] = (counts["投稿数"] / total_yandere_videos * 100).round(1)
    
    md_table = counts.to_markdown(index=False)
    
    header = "# 2025年 ヤンデレ動画 キャラクター投稿数ランキング (software_talk全体)\n\n"
    summary = f"集計対象: 2025年に投稿され、タイトルまたはタグに「ヤンデレ」を含む動画\n"
    summary += f"総ヤンデレ動画数: {total_yandere_videos}\n\n"
    
    output_path = "results/yandere_character_ranking.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(header + summary + md_table)
    
    print(f"\nResults saved to {output_path}")
    print("\n" + header + summary + md_table)

if __name__ == "__main__":
    main()
