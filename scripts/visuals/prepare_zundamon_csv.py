# /// script
# dependencies = [
#   "pandas",
# ]
# ///

import pickle
import pandas as pd
from pathlib import Path
from common_utils import filter_software_talk, find_characters

def prepare_csv():
    target_character = "ずんだもん"
    cat = "software_talk"
    
    characters_df = pd.read_csv("characters.csv")
    character_names = characters_df["キャラクター名"].tolist()

    pickle_path = Path(f"results/{cat}.pickle")
    if not pickle_path.exists():
        print(f"Error: {pickle_path} not found.")
        return
        
    print(f"Loading {pickle_path}...")
    with open(pickle_path, "rb") as f:
        recv = pickle.load(f)
    df = pd.json_normalize(recv["data"])
    
    df = filter_software_talk(df)
        
    df["startTime"] = pd.to_datetime(df["startTime"])
    df["year"] = df["startTime"].dt.year
    df["viewCounter"] = df["viewCounter"].astype(int)
    
    # Up to 2025
    df = df[df["year"] <= 2025]
    
    print("Finding characters in tags...")
    df["found_characters"] = df["tags"].apply(lambda x: find_characters(x, character_names))
    
    # Filter for Zundamon
    zundamon_df = df[df["found_characters"].apply(lambda chars: target_character in chars)]
    
    # Group by year
    yearly_stats = zundamon_df.groupby("year")["viewCounter"].sum().reset_index()
    
    # Ensure all years from 2020 to 2025 are present
    all_years = pd.DataFrame({"year": range(2020, 2026)})
    yearly_stats = pd.merge(all_years, yearly_stats, on="year", how="left").fillna(0)
    
    yearly_stats["cumulativeViewCounter"] = yearly_stats["viewCounter"].cumsum().astype(int)
    yearly_stats["viewCounter"] = yearly_stats["viewCounter"].astype(int)
    yearly_stats["year_int"] = yearly_stats["year"]
    
    output_path = "results/zundamon_cumulative_stats_software_talk_2020.csv"
    yearly_stats.to_csv(output_path, index=False)
    print(f"Saved yearly stats to {output_path}")
    print(yearly_stats)

if __name__ == "__main__":
    prepare_csv()
