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
全ジャンルおよび各ジャンル個別のキャラクター別再生数ランキングの歴史的推移を分析します。
年ごとの順位変動をバンプチャート（順位推移図）として可視化し、
どの時期にどのキャラクターが人気を集めていたかの変遷を明らかにします。
"""

import pickle
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import matplotlib_fontja
import seaborn as sns
from pathlib import Path

from common_utils import filter_software_talk

# 日本語フォント設定
# matplotlib_fontja.japanize() # Main execution blockで設定します

def load_characters():
    df = pd.read_csv("characters.csv")
    return df["キャラクター名"].tolist()

def find_characters(tags, character_names):
    if not tags:
        return []
    
    # タグリストの正規化
    if isinstance(tags, str):
        tag_list = tags.split()
        tags_str = tags
    elif isinstance(tags, list):
        tag_list = tags
        tags_str = " ".join(tags)
    else:
        return []
        
    found = []
    # 完全一致が必要な短い名前のキャラなど
    exact_match_chars = ["RIA", "朱花", "青葉", "銀芽", "金苗", "ナツ", "シロ", "ナコ", "レコ"]
    
    for name in character_names:
        if name in exact_match_chars:
            if name in tag_list:
                found.append(name)
        else:
            # 部分一致 (タグ文字列の中にキャラ名が含まれるか)
            if name in tags_str:
                found.append(name)
    return found

def process_genre(category, character_names, use_cache=True):
    cache_dir = Path("results/history/cache")
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / f"{category}_processed.csv"

    if use_cache and cache_path.exists():
        print(f"Loading cached data for {category}...")
        df_cached = pd.read_csv(cache_path)
        # startTimeをdatetime型に戻す
        if "startTime" in df_cached.columns:
            df_cached["startTime"] = pd.to_datetime(df_cached["startTime"])
        return df_cached

    pickle_path = Path(f"results/{category}.pickle")
    if not pickle_path.exists():
        print(f"Skipping {category}: File not found.")
        return pd.DataFrame()

    print(f"Processing {category}...")
    with open(pickle_path, "rb") as f:
        recv = pickle.load(f)
    
    df = pd.json_normalize(recv["data"])
    
    # ソフトウェアトークの場合、VOCALOID関連および音楽関連を除外 (analyzer.pyと同等のフィルタ)
    if category == "software_talk":
        df = filter_software_talk(df)

    df["startTime"] = pd.to_datetime(df["startTime"])
    df["year"] = df["startTime"].dt.year.astype(int)
    df["viewCounter"] = df["viewCounter"].astype(int)

    # キャラクター抽出
    # 高速化のため、タグのユニークな組み合わせに対してキャラ抽出を行い、マージする
    df["tags_str"] = df["tags"].apply(lambda x: " ".join(x) if isinstance(x, list) else str(x))
    unique_tags = df[["tags_str"]].drop_duplicates()
    unique_tags["found_chars"] = unique_tags["tags_str"].apply(lambda x: find_characters(x, character_names))
    
    df = df.merge(unique_tags, on="tags_str", how="left")
    
    # 展開 (1動画に複数キャラがいる場合、それぞれに行を分ける)
    df_exploded = df.explode("found_chars")
    df_exploded = df_exploded.dropna(subset=["found_chars"])
    df_exploded = df_exploded.rename(columns={"found_chars": "character"})
    
    # プロットに必要なカラムのみ抽出
    res_df = df_exploded[["year", "character", "viewCounter", "contentId", "startTime"]]
    
    # キャッシュ保存
    res_df.to_csv(cache_path, index=False, encoding="utf-8-sig")
    
    return res_df

def create_bump_chart(df_pivot_rank, title, output_path, top_n=10):
    # カラム（年）を数値型に変換
    df_pivot_rank.columns = df_pivot_rank.columns.astype(int)

    # 最新年の上位N人を取得
    last_year = df_pivot_rank.columns.max()
    # 最新年にデータがないキャラがいる可能性を考慮し、ドロップナ
    last_year_data = df_pivot_rank[last_year].dropna().sort_values()
    top_chars = last_year_data.head(top_n).index.tolist()
    
    # 過去に1位を取ったことがあるキャラも追加 (歴史的勝者)
    leaders = df_pivot_rank.apply(lambda x: x.idxmin(), axis=0).dropna().unique().tolist()
    
    target_chars = list(set(top_chars + leaders))
    
    # フィルタリング
    df_plot = df_pivot_rank.loc[target_chars]
    
    plt.figure(figsize=(16, 10))
    
    # カラーパレット
    palette = sns.color_palette("tab20", len(target_chars))
    char_colors = dict(zip(target_chars, palette))

    # 特別なキャラの色固定 (公式イメージカラー等に基づく)
    special_colors = {
        "結月ゆかり": "#a05daf", # 紫
        "紲星あかり": "#f8b500", # オレンジ
        "琴葉茜": "#ea5b76",     # 赤・ピンク
        "琴葉葵": "#3a8fb7",     # 青
        "弦巻マキ": "#d03030",   # 赤 (マキ) - 少し赤く
        "東北きりたん": "#A52A2A", # 茶 (元の色)
        "ずんだもん": "#32CD32", # 緑
        "東北ずん子": "#7eba81", # 緑
        "東北イタコ": "#98d98e", # 黄緑
        "四国めたん": "#e03c60", # 濃いピンク
        "春日部つむぎ": "#d4a017", # 濃いめの黄色 (視認性向上)
        "雨晴はう": "#5fb3d4",   # 濃いめの水色 (視認性向上)
        "冥鳴ひまり": "#e66ab0", # 濃いめのピンク (視認性向上)
        "重音テト": "#d7003a",   # 赤
        "可不": "#007bbb",       # 濃いめの青 (視認性向上)
        "足立レイ": "#ff4500",   # オレンジ
    }
    for char, color in special_colors.items():
        if char in char_colors:
            char_colors[char] = color

    # 文字をはっきりさせるための黒の縁取り (削除)
    pe = []

    for char in df_plot.index:
        data = df_plot.loc[char].copy()
        # 10位以下は11位として扱い、表示範囲外にする
        data[data > 10] = 11
        
        # プロット
        plt.plot(data.index, data.values, marker='o', linewidth=4, label=char, color=char_colors[char], alpha=0.8)
        
        # 始点と終点に名前を表示
        valid_data = data[data <= 10] # 10位以内のデータのみ
        if not valid_data.empty:
             first_visible_year = valid_data.index[0]
             last_visible_year = valid_data.index[-1]
             max_year = df_pivot_rank.columns.max()
             
             # 左側ラベル: 2025年より前に初めて登場した場合、その初登場年の左側に表示
             if first_visible_year < max_year:
                plt.text(first_visible_year - 0.3, data[first_visible_year], char, ha='right', va='center', 
                         fontsize=15, color=char_colors[char], weight='bold', path_effects=pe)
             
             # 右側ラベル: 最後に登場した年の右側に表示
             # (2025年初登場の場合、または複数年にわたって登場している場合)
             if first_visible_year == max_year or last_visible_year > first_visible_year:
                plt.text(last_visible_year + 0.3, data[last_visible_year], char, ha='left', va='center', 
                         fontsize=15, color=char_colors[char], weight='bold', path_effects=pe)

    plt.gca().invert_yaxis() # 1位を上に
    plt.yticks(range(1, 11)) # 1位〜10位まで目盛
    plt.ylim(10.5, 0.5) # 表示範囲 (10位まで表示)
    
    plt.title(title, fontsize=20)
    plt.xlabel("年", fontsize=14)
    plt.ylabel("順位 (再生数)", fontsize=14)
    plt.grid(True, axis='x', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()

def main():
    target_categories = ["game", "onboard", "explanation", "kitchen", "theater", "travel", "fishing"]
    output_dir = Path("results/history")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    character_names = load_characters()
    
    # 1. 全体データの処理 (software_talk を使用)
    print("Processing overall data (software_talk)...")
    df_overall_raw = process_genre("software_talk", character_names)
    if not df_overall_raw.empty:
        df_overall_raw = df_overall_raw[(df_overall_raw["year"] >= 2011) & (df_overall_raw["year"] <= 2025)]
        
        # ノイズ除去
        df_overall_raw = df_overall_raw[~((df_overall_raw["character"] == "東北イタコ") & (df_overall_raw["year"] == 2013))]
        
        print("Generating overall ranking...")
        yearly_views = df_overall_raw.groupby(["year", "character"])["viewCounter"].sum().reset_index()
        df_wide_views = yearly_views.pivot(index="year", columns="character", values="viewCounter")
        df_wide_views.to_csv(output_dir / "overall_views_race.csv", encoding="utf-8-sig")
        
        df_rank = df_wide_views.rank(axis=1, ascending=False, method='min')
        
        sns.set_style("whitegrid")
        try:
            matplotlib_fontja.japanize()
        except:
            import platform
            if platform.system() == "Windows":
                plt.rcParams['font.family'] = ['Meiryo', 'Yu Gothic', 'MS Gothic']
        
        create_bump_chart(df_rank.T, "ボイロキャラクター人気順位推移 (全体)", output_dir / "bump_chart_overall.png")

    # 2. ジャンル別データの処理
    for genre in target_categories:
        df_genre = process_genre(genre, character_names)
        if df_genre.empty:
            continue
            
        df_genre = df_genre[(df_genre["year"] >= 2011) & (df_genre["year"] <= 2025)]
        
        print(f"Generating ranking for {genre}...")
        yearly_views_g = df_genre.groupby(["year", "character"])["viewCounter"].sum().reset_index()
        df_wide_views_g = yearly_views_g.pivot(index="year", columns="character", values="viewCounter")
        df_wide_views_g.to_csv(output_dir / f"{genre}_views_race.csv", encoding="utf-8-sig")
        
        df_rank_g = df_wide_views_g.rank(axis=1, ascending=False, method='min')
        create_bump_chart(df_rank_g.T, f"ボイロキャラクター人気順位推移 ({genre})", output_dir / f"bump_chart_{genre}.png")

    print("Done. Check results/history/")


if __name__ == "__main__":
    main()
