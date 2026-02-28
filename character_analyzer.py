# /// script
# dependencies = [
#   "matplotlib",
#   "matplotlib-fontja",
#   "pandas",
#   "scipy",
#   "seaborn",
# ]
# ///

"""
Processing Overview:
分析対象のカテゴリ（実況、車載など）を受け取り、動画のタグから出演キャラクターを抽出します。
抽出したデータを基に、キャラクター別の総再生数ランキング、年別ランキング、
および2人出演限定のコンビランキングを集計し、グラフ（ランキング図、推移図）として可視化します。
"""

import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib_fontja
import sys
from pathlib import Path

from common_utils import filter_software_talk, find_characters

matplotlib_fontja.japanize()

def main(category):
    pickle_path = Path(f"results/{category}.pickle")
    characters_path = Path("characters.csv")
    output_dir = Path("results") / category
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load data
    print(f"Loading data for {category}...")
    with open(pickle_path, "rb") as f:
        recv = pickle.load(f)
    df = pd.json_normalize(recv["data"])

    # ソフトウェアトークの場合、VOCALOID関連を除外（歌唱系が混じるため）
    if category == "software_talk":
        df = filter_software_talk(df)

    df["startTime"] = pd.to_datetime(df["startTime"])
    df["year"] = df["startTime"].dt.year
    df["viewCounter"] = df["viewCounter"].astype(int)

    characters_df = pd.read_csv(characters_path)
    character_names = characters_df["キャラクター名"].tolist()

    # 2. Map characters to videos
    print(f"Mapping characters to videos for {category}...")
    df["found_characters"] = df["tags"].apply(lambda x: find_characters(x, character_names))

    # 3. Save mapping
    print("Saving mapping...")
    mapping_data = []
    for _, row in df.iterrows():
        for char in row["found_characters"]:
            mapping_data.append({
                "contentId": row["contentId"],
                "character": char,
                "viewCounter": row["viewCounter"],
                "year": row["year"]
            })
    
    if not mapping_data:
        print(f"No characters found for {category}.")
        return
        
    mapping_df = pd.DataFrame(mapping_data)
    mapping_df.to_csv(output_dir / f"{category}_character_mapping.csv", index=False, encoding="utf-8-sig")

    # 4. Calculate rankings
    print("Calculating view rankings...")
    char_views = mapping_df.groupby("character")["viewCounter"].sum().sort_values(ascending=False).reset_index()
    char_views.to_csv(output_dir / f"{category}_character_ranking_overall.csv", index=False, encoding="utf-8-sig")

    # 5. Visualization - Rankings
    print("Visualizing rankings...")
    plt.figure(figsize=(12, 8))
    top_overall = char_views.head(20)
    sns.barplot(data=top_overall, x="viewCounter", y="character", hue="character", palette="viridis", legend=False)
    plt.title(f"{category} キャラクター別総再生数ランキング (TOP 20)")
    plt.tight_layout()
    plt.savefig(output_dir / f"{category}_character_ranking_overall.png")
    plt.close()

    # 5b. Yearly Rankings (Top 20 per year)
    print("Visualizing yearly rankings...")
    all_years = [y for y in range(2017, 2026)]
    fig, axes = plt.subplots(3, 3, figsize=(24, 20))
    axes = axes.flatten()
    
    for i, year in enumerate(all_years):
        year_data = mapping_df[mapping_df["year"] == year].groupby("character")["viewCounter"].sum().sort_values(ascending=False).head(20).reset_index()
        if not year_data.empty:
            sns.barplot(data=year_data, x="viewCounter", y="character", ax=axes[i], hue="character", palette="magma", legend=False)
            axes[i].set_title(f"{year}年 (TOP 20)", fontsize=16)
            axes[i].set_xlabel("再生数")
            axes[i].set_ylabel("")
        else:
            axes[i].set_title(f"{year}年 (データなし)", fontsize=16)
    plt.tight_layout()
    plt.savefig(output_dir / f"{category}_character_ranking_yearly.png")
    plt.close()

    # 6. Co-occurrence Matrix
    print("Creating co-occurrence matrix...")
    co_occurrence = np.zeros((len(character_names), len(character_names)))
    char_to_idx = {name: i for i, name in enumerate(character_names)}

    for found in df["found_characters"]:
        for i in range(len(found)):
            for j in range(i + 1, len(found)):
                idx1 = char_to_idx[found[i]]
                idx2 = char_to_idx[found[j]]
                co_occurrence[idx1, idx2] += 1
                co_occurrence[idx2, idx1] += 1

    co_df = pd.DataFrame(co_occurrence, index=character_names, columns=character_names)
    mask = co_df.sum(axis=0) > 0
    co_df_filtered = co_df.loc[mask, mask]

    # 9. Co-occurrence Network & Pairings
    print("Visualizing network and pairings...")
    if not co_df_filtered.empty:
        # Top Pairings by view count (Strictly 2 characters)
        pair_views = {}
        for _, row in df.iterrows():
            found = row["found_characters"]
            if len(found) == 2:
                p = sorted(found)
                pair_name = f"{p[0]} & {p[1]}"
                pair_views[pair_name] = pair_views.get(pair_name, 0) + row["viewCounter"]
        
        if pair_views:
            top_pairs = pd.Series(pair_views).sort_values(ascending=False).head(20)
            plt.figure(figsize=(10, 8))
            sns.barplot(x=top_pairs.values, y=top_pairs.index, hue=top_pairs.index, palette="coolwarm", legend=False)
            plt.title(f"{category} 人気コンビ総再生数ランキング (TOP 20 - 2人出演限定)")
            plt.xlabel("再生数")
            plt.tight_layout()
            plt.savefig(output_dir / f"{category}_top_pairings_ranking.png")
            plt.close()

        # Yearly Top Pairings by view count (Strictly 2 characters)
        print("Visualizing yearly pairings...")
        fig, axes = plt.subplots(3, 3, figsize=(24, 20))
        axes = axes.flatten()
        
        for i, year in enumerate(all_years):
            year_df = df[df["year"] == year]
            pair_views_year = {}
            for _, row in year_df.iterrows():
                found = row["found_characters"]
                if len(found) == 2:
                    p = sorted(found)
                    pair_name = f"{p[0]} & {p[1]}"
                    pair_views_year[pair_name] = pair_views_year.get(pair_name, 0) + row["viewCounter"]
            
            if pair_views_year:
                top_pairs_year = pd.Series(pair_views_year).sort_values(ascending=False).head(20)
                sns.barplot(x=top_pairs_year.values, y=top_pairs_year.index, ax=axes[i], hue=top_pairs_year.index, palette="coolwarm", legend=False)
                axes[i].set_title(f"{year}年 (TOP 20 - 2人出演限定)", fontsize=16)
                axes[i].set_xlabel("再生数")
                axes[i].set_ylabel("")
            else:
                axes[i].set_title(f"{year}年 (データなし)", fontsize=16)
        
        plt.tight_layout()
        plt.savefig(output_dir / f"{category}_top_pairings_ranking_yearly.png")
        plt.close()

    print("Done.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main("onboard")
