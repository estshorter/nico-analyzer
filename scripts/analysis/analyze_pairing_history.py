# /// script
# dependencies = [
#   "matplotlib",
#   "matplotlib-fontja",
#   "pandas",
#   "seaborn",
# ]
# ///

"""
Processing Overview:
指定したジャンル（デフォルトはゲーム実況）におけるキャラクターペア（コンビ）の人気推移を分析します。
動画タグから2人以上のキャラクターが含まれる動画を抽出し、ペアごとの合計再生数を年単位で集計。
人気ペアの順位変動をバンプチャートとして可視化します。
"""

import pickle
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib_fontja
import seaborn as sns
from pathlib import Path
from itertools import combinations
import sys

# 日本語フォント設定
# matplotlib_fontja.japanize() # Main execution blockで設定します

def load_characters():
    df = pd.read_csv("characters.csv")
    return df["キャラクター名"].tolist()

def find_characters(tags, character_names):
    if not tags:
        return []
    
    if isinstance(tags, str):
        tag_list = tags.split()
        tags_str = tags
    elif isinstance(tags, list):
        tag_list = tags
        tags_str = " ".join(tags)
    else:
        return []
        
    found = []
    exact_match_chars = ["RIA", "朱花", "青葉", "銀芽", "金苗", "ナツ", "シロ", "ナコ", "レコ"]
    
    for name in character_names:
        if name in exact_match_chars:
            if name in tag_list:
                found.append(name)
        else:
            if name in tags_str:
                found.append(name)
    return found

def create_bump_chart(df_pivot_rank, title, output_path, top_n=15):
    # カラム（年）を数値型に変換
    df_pivot_rank.columns = df_pivot_rank.columns.astype(int)

    # 最新年の上位Nペアを取得
    last_year = df_pivot_rank.columns.max()
    top_pairs = df_pivot_rank[last_year].sort_values().head(top_n).index.tolist()
    
    # 過去に1位を取ったことがあるペアも追加
    leaders = df_pivot_rank.apply(lambda x: x.idxmin(), axis=0).unique().tolist()
    
    target_pairs = list(set(top_pairs + leaders))
    
    # フィルタリング
    df_plot = df_pivot_rank.loc[target_pairs]
    
    plt.figure(figsize=(16, 12))
    
    # カラーパレット
    palette = sns.color_palette("tab20", len(target_pairs))
    pair_colors = dict(zip(target_pairs, palette))

    # 特定のペアの色を固定（視認性向上）
    # ゆかり・マキ: Purple
    # 茜・葵: Pink
    # ゆかり・あかり: Orange
    # ずんだもん・めたん: Green
    
    for pair in target_pairs:
        if "結月ゆかり" in pair and "弦巻マキ" in pair:
            pair_colors[pair] = "#800080" # Purple
        elif "琴葉茜" in pair and "琴葉葵" in pair:
            pair_colors[pair] = "#FF69B4" # Pink
        elif "結月ゆかり" in pair and "紲星あかり" in pair:
            pair_colors[pair] = "#FFA500" # Orange
        elif "ずんだもん" in pair and "四国めたん" in pair:
            pair_colors[pair] = "#32CD32" # Green
        elif "東北きりたん" in pair and "東北ずん子" in pair:
            pair_colors[pair] = "#2E8B57" # SeaGreen

    for pair in df_plot.index:
        data = df_plot.loc[pair].copy()
        
        # 20位以下は21位として扱う（グラフの下底に張り付かせる）
        data[data > 20] = 21
        
        # Plot
        width = 4
        if pair_colors.get(pair) in ["#800080", "#FF69B4", "#FFA500", "#32CD32"]:
            width = 6 # Main pairs thicker
            
        plt.plot(data.index, data.values, marker='o', linewidth=width, label=pair, color=pair_colors[pair], alpha=0.8)
        
        # Labels
        valid_data = data.dropna()
        if not valid_data.empty:
             # Start label
             start_idx = valid_data.index[0]
             plt.text(start_idx - 0.2, valid_data.loc[start_idx], pair, ha='right', va='center', fontsize=9, color=pair_colors[pair], weight='bold')
             # End label
             end_idx = valid_data.index[-1]
             plt.text(end_idx + 0.2, valid_data.loc[end_idx], pair, ha='left', va='center', fontsize=12, color=pair_colors[pair], weight='bold')

    plt.gca().invert_yaxis()
    plt.yticks(range(1, 21))
    plt.ylim(21.5, 0.5)
    
    plt.title(title, fontsize=20)
    plt.xlabel("年", fontsize=14)
    plt.ylabel("順位 (再生数)", fontsize=14)
    plt.grid(True, axis='x', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()

def main():
    genre = "game" # Default target
    output_dir = Path("results/history")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    character_names = load_characters()
    
    pickle_path = Path(f"results/{genre}.pickle")
    if not pickle_path.exists():
        print(f"File not found: {pickle_path}")
        return

    print(f"Processing {genre} for Pairings...")
    with open(pickle_path, "rb") as f:
        recv = pickle.load(f)
    
    df = pd.json_normalize(recv["data"])
    df["startTime"] = pd.to_datetime(df["startTime"])
    df["year"] = df["startTime"].dt.year.astype(int)
    df["viewCounter"] = df["viewCounter"].astype(int)
    
    # 2011-2025
    df = df[(df["year"] >= 2011) & (df["year"] <= 2025)]

    # Extract chars per video
    # Optimization: Unique tags first
    df["tags_str"] = df["tags"].apply(lambda x: " ".join(x) if isinstance(x, list) else str(x))
    unique_tags = df[["tags_str"]].drop_duplicates()
    unique_tags["found_chars"] = unique_tags["tags_str"].apply(lambda x: find_characters(x, character_names))
    
    df = df.merge(unique_tags, on="tags_str", how="left")
    
    # Expand Pairs
    pair_data = []
    
    print("Aggregating pairs...")
    for _, row in df.iterrows():
        chars = row["found_chars"]
        if len(chars) >= 2:
            # Sort to ensure "A & B" is same as "B & A"
            for p in combinations(sorted(chars), 2):
                pair_name = f"{p[0]} & {p[1]}"
                pair_data.append({
                    "year": row["year"],
                    "pair": pair_name,
                    "viewCounter": row["viewCounter"]
                })
    
    if not pair_data:
        print("No pairs found.")
        return
        
    df_pairs = pd.DataFrame(pair_data)
    
    # Group by Year + Pair
    yearly_pair_views = df_pairs.groupby(["year", "pair"])["viewCounter"].sum().reset_index()
    
    # Pivot
    df_wide = yearly_pair_views.pivot(index="year", columns="pair", values="viewCounter")
    df_wide.to_csv(output_dir / f"{genre}_pairings_race.csv", encoding="utf-8-sig")
    
    # Rank
    df_rank = df_wide.rank(axis=1, ascending=False, method='min')
    
    # Plot
    sns.set_style("whitegrid")
    try:
        matplotlib_fontja.japanize()
    except:
        import platform
        if platform.system() == "Windows":
            plt.rcParams['font.family'] = ['Meiryo', 'Yu Gothic', 'MS Gothic']

    create_bump_chart(df_rank.T, f"ボイロ実況 人気ペア推移 ({genre})", output_dir / f"bump_chart_{genre}_pairs.png")
    
    print(f"Done. Saved to {output_dir / f'bump_chart_{genre}_pairs.png'}")

if __name__ == "__main__":
    main()
