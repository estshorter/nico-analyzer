# /// script
# dependencies = [
#   "pandas",
# ]
# ///

import pickle
from pathlib import Path
import pandas as pd

def preprocess(category):
    pickle_path = Path(f"results/{category}.pickle")
    if not pickle_path.exists():
        return None
    with open(pickle_path, "rb") as f:
        recv = pickle.load(f)
    df = pd.json_normalize(recv["data"])
    df["startTime"] = pd.to_datetime(df["startTime"])
    df["year"] = df["startTime"].dt.year
    return df

def main():
    category = "explanation"
    target_user_id = 5482382
    df = preprocess(category)
    if df is None: return

    user_id_col = "userId" if "userId" in df.columns else "owner.id"
    df_user = df[df[user_id_col] == target_user_id].sort_values("startTime", ascending=False)

    titles = df_user["title"].head(100).tolist()
    
    output_path = Path("results/explanation/user_5482382_titles.txt")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        for title in titles:
            f.write(f"{title}\n")
            
    print(f"Extracted {len(titles)} titles to {output_path}")

if __name__ == "__main__":
    main()
