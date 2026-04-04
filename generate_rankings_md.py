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

def get_top_20(category):
    pickle_path = Path(f"results/{category}.pickle")
    if not pickle_path.exists():
        print(f"Warning: {pickle_path} not found.")
        return None
        
    with open(pickle_path, "rb") as f:
        recv = pickle.load(f)
    df = pd.json_normalize(recv["data"])
    
    if category == "software_talk":
        df = filter_software_talk(df)
        
    df["startTime"] = pd.to_datetime(df["startTime"])
    df["year"] = df["startTime"].dt.year
    
    # 2025年12月31日までのデータに限定（必要に応じて）
    df = df[df["year"] <= 2025]
    
    characters_df = pd.read_csv("characters.csv")
    character_names = characters_df["キャラクター名"].tolist()
    
    df["found_characters"] = df["tags"].apply(lambda x: find_characters(x, character_names))
    
    # Explode to get character mapping
    mapping_data = []
    for _, row in df.iterrows():
        for char in row["found_characters"]:
            mapping_data.append({
                "contentId": row["contentId"],
                "character": char
            })
            
    if not mapping_data:
        return None
        
    m_df = pd.DataFrame(mapping_data)
    # 投稿数（contentIdのユニーク数）
    counts = m_df.groupby("character")["contentId"].nunique().sort_values(ascending=False).head(20).reset_index()
    counts.columns = ["キャラクター", "投稿数"]
    return counts

def main():
    categories = ["software_talk", "game", "onboard", "kitchen", "explanation", "theater", "travel"]
    cat_names = {
        "software_talk": "ソフトウェアトーク全体",
        "game": "実況",
        "onboard": "車載",
        "kitchen": "キッチン",
        "explanation": "解説",
        "theater": "劇場",
        "travel": "旅行"
    }
    
    output_lines = ["# キャラクター投稿数ランキング TOP 20", ""]
    
    for cat in categories:
        print(f"Processing {cat}...")
        top_20 = get_top_20(cat)
        if top_20 is not None:
            output_lines.append(f"## {cat_names[cat]}")
            output_lines.append("")
            output_lines.append(top_20.to_markdown(index=False))
            output_lines.append("")
            
    with open("results/top_20_rankings.md", "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
    print("Done! Saved to results/top_20_rankings.md")
    print("\n".join(output_lines))

if __name__ == "__main__":
    main()
