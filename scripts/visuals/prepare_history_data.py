# /// script
# dependencies = [
#   "pandas",
# ]
# ///
import pickle
import pandas as pd
from pathlib import Path
from common_utils import filter_software_talk, find_characters

def process_category(category):
    pickle_path = Path(f"results/{category}.pickle")
    output_dir = Path("results/history/cache")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{category}_processed.csv"
    
    if not pickle_path.exists():
        print(f"Warning: {pickle_path} not found.")
        return
        
    print(f"Loading {category}...")
    with open(pickle_path, "rb") as f:
        recv = pickle.load(f)
    df = pd.json_normalize(recv["data"])
    
    if category == "software_talk":
        df = filter_software_talk(df)
        
    df["startTime"] = pd.to_datetime(df["startTime"])
    df["year"] = df["startTime"].dt.year
    
    characters_df = pd.read_csv("characters.csv")
    character_names = characters_df["キャラクター名"].tolist()
    
    print(f"Mapping characters for {category}...")
    df["found_characters"] = df["tags"].apply(lambda x: find_characters(x, character_names))
    
    mapping_data = []
    for _, row in df.iterrows():
        for char in row["found_characters"]:
            mapping_data.append({
                "year": row["year"],
                "character": char,
                "contentId": row["contentId"]
            })
            
    if not mapping_data:
        print(f"No data for {category}")
        return
        
    m_df = pd.DataFrame(mapping_data)
    m_df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"Saved to {output_path}")

def main():
    categories = ["software_talk", "game", "onboard", "kitchen", "explanation", "theater", "travel"]
    for cat in categories:
        process_category(cat)

if __name__ == "__main__":
    main()
