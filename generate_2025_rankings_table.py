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

def get_top_20_2025(category):
    pickle_path = Path(f"results/{category}.pickle")
    if not pickle_path.exists():
        return None
        
    with open(pickle_path, "rb") as f:
        recv = pickle.load(f)
    df = pd.json_normalize(recv["data"])
    
    if category == "software_talk":
        df = filter_software_talk(df)
        
    df["startTime"] = pd.to_datetime(df["startTime"])
    df["year"] = df["startTime"].dt.year
    df_2025 = df[df["year"] == 2025]
    
    characters_df = pd.read_csv("characters.csv")
    character_names = characters_df["キャラクター名"].tolist()
    
    df_2025["found_characters"] = df_2025["tags"].apply(lambda x: find_characters(x, character_names))
    
    mapping_data = []
    for _, row in df_2025.iterrows():
        for char in row["found_characters"]:
            mapping_data.append({"character": char, "contentId": row["contentId"]})
            
    if not mapping_data:
        return None
        
    m_df = pd.DataFrame(mapping_data)
    counts = m_df.groupby("character")["contentId"].nunique().sort_values(ascending=False).head(30).reset_index()
    counts.columns = ["キャラクター", "投稿数"]
    return counts

def main():
    # Requested order: 全体(software_talk), 実況(game), 劇場(theater), 解説(explanation), キッチン(kitchen), 車載(onboard), 旅行(travel)
    categories = ["software_talk", "game", "theater", "explanation", "kitchen", "onboard", "travel"]
    cat_names = {
        "software_talk": "全体",
        "game": "実況",
        "theater": "劇場",
        "explanation": "解説",
        "kitchen": "キッチン",
        "onboard": "車載",
        "travel": "旅行"
    }
    
    all_ranks = {}
    for cat in categories:
        print(f"Processing {cat} for 2025...")
        top_20 = get_top_20_2025(cat)
        if top_20 is not None:
            # Format as "Char (Count)"
            all_ranks[cat_names[cat]] = [f"{row['キャラクター']} ({row['投稿数']})" for _, row in top_20.iterrows()]
        else:
            all_ranks[cat_names[cat]] = ["-"] * 30

    # Ensure all lists are length 30
    for cat in all_ranks:
        while len(all_ranks[cat]) < 30:
            all_ranks[cat].append("-")

    res_df = pd.DataFrame(all_ranks)
    res_df.index = range(1, 31)
    res_df.index.name = "順位"
    
    md_table = res_df.to_markdown()
    
    header = "# 2025年 キャラクター投稿数ランキング TOP 20 (ジャンル別比較)\n\n"
    footer = "\n\n※ 投稿数は2025年の1年間のユニーク動画数です。"
    
    with open("results/top_20_2025_comparison.md", "w", encoding="utf-8") as f:
        f.write(header + md_table + footer)
    
    print("\n" + header + md_table + footer)

if __name__ == "__main__":
    main()
