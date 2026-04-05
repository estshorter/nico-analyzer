# /// script
# dependencies = [
#   "matplotlib",
#   "matplotlib-fontja",
#   "pandas",
#   "seaborn",
#   "tabulate",
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
    cache_path = cache_dir / f"{category}_processed_v2.csv" # V2 to include userId

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
    # userIdが欠損している場合は0または適当な値で埋める (一応)
    if "userId" not in df.columns:
        df["userId"] = 0
    df["userId"] = df["userId"].fillna(0).astype(int)

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
    res_df = df_exploded[["year", "character", "viewCounter", "contentId", "startTime", "userId"]]
    
    # キャッシュ保存
    res_df.to_csv(cache_path, index=False, encoding="utf-8-sig")
    
    return res_df

def create_bump_chart(df_pivot_rank, title, output_path, ylabel="順位", top_n=10):
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
                         fontsize=15, color=char_colors[char], weight='bold')
             
             # 右側ラベル: 最後に登場した年の右側に表示
             if first_visible_year == max_year or last_visible_year > first_visible_year:
                plt.text(last_visible_year + 0.3, data[last_visible_year], char, ha='left', va='center', 
                         fontsize=15, color=char_colors[char], weight='bold')

    plt.gca().invert_yaxis() # 1位を上に
    plt.yticks(range(1, 11)) # 1位〜10位まで目盛
    plt.ylim(10.5, 0.5) # 表示範囲 (10位まで表示)
    
    plt.title(title, fontsize=20)
    plt.xlabel("年", fontsize=14)
    plt.ylabel(ylabel, fontsize=14)
    plt.grid(True, axis='x', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()

def save_rankings_summary(df_raw, genre, output_dir):
    # 2025年のランキングサマリーを作成
    df_2025 = df_raw[df_raw["year"] == 2025]
    if df_2025.empty:
        return

    # 各指標の集計
    stats = df_2025.groupby("character").agg({
        "contentId": "nunique",
        "userId": "nunique",
        "viewCounter": "sum"
    }).reset_index()
    
    stats.columns = ["キャラクター", "投稿数", "投稿者数", "再生数"]
    stats["1人あたり平均投稿数"] = (stats["投稿数"] / stats["投稿者数"]).round(2)
    
    # 投稿数でソート
    stats_posts = stats.sort_values("投稿数", ascending=False).head(20)
    
    # 投稿者数でソート
    stats_posters = stats.sort_values("投稿者数", ascending=False).head(20)
    
    output_path = output_dir / f"ranking_summary_2025_{genre}.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"# 2025年 キャラクターランキングサマリー ({genre})\n\n")
        f.write("## 投稿数ランキング (TOP 20)\n")
        f.write(stats_posts[["キャラクター", "投稿数", "投稿者数", "1人あたり平均投稿数", "再生数"]].to_markdown(index=False))
        f.write("\n\n")
        f.write("## 投稿者数ランキング (TOP 20)\n")
        f.write(stats_posters[["キャラクター", "投稿者数", "投稿数", "1人あたり平均投稿数", "再生数"]].to_markdown(index=False))
        f.write("\n")
    
    print(f"Saved summary to {output_path}")

def generate_all_rankings(df_raw, category, output_dir, title_suffix):
    if df_raw.empty:
        return
        
    df_raw = df_raw[(df_raw["year"] >= 2011) & (df_raw["year"] <= 2025)]
    if df_raw.empty:
        return

    # 1. 再生数
    print(f"Generating views ranking for {category}...")
    yearly_views = df_raw.groupby(["year", "character"])["viewCounter"].sum().reset_index()
    df_wide_views = yearly_views.pivot(index="year", columns="character", values="viewCounter")
    df_wide_views.to_csv(output_dir / f"{category}_views_race.csv", encoding="utf-8-sig")
    df_rank_views = df_wide_views.rank(axis=1, ascending=False, method='min')
    create_bump_chart(df_rank_views.T, f"ボイロキャラ人気推移:再生数 ({title_suffix})", output_dir / f"bump_chart_{category}_views.png", ylabel="順位 (再生数)")

    # 2. 投稿数
    print(f"Generating posts ranking for {category}...")
    yearly_posts = df_raw.groupby(["year", "character"])["contentId"].nunique().reset_index()
    df_wide_posts = yearly_posts.pivot(index="year", columns="character", values="contentId")
    df_wide_posts.to_csv(output_dir / f"{category}_posts_race.csv", encoding="utf-8-sig")
    df_rank_posts = df_wide_posts.rank(axis=1, ascending=False, method='min')
    create_bump_chart(df_rank_posts.T, f"ボイロキャラ人気推移:投稿数 ({title_suffix})", output_dir / f"bump_chart_{category}_posts.png", ylabel="順位 (投稿数)")

    # 3. 投稿者数
    print(f"Generating posters ranking for {category}...")
    yearly_posters = df_raw.groupby(["year", "character"])["userId"].nunique().reset_index()
    df_wide_posters = yearly_posters.pivot(index="year", columns="character", values="userId")
    df_wide_posters.to_csv(output_dir / f"{category}_posters_race.csv", encoding="utf-8-sig")
    df_rank_posters = df_wide_posters.rank(axis=1, ascending=False, method='min')
    create_bump_chart(df_rank_posters.T, f"ボイロキャラ人気推移:投稿者数 ({title_suffix})", output_dir / f"bump_chart_{category}_posters.png", ylabel="順位 (投稿者数)")

    # 4. 平均投稿数 (CSVのみ)
    yearly_avg = (df_wide_posts / df_wide_posters).round(2)
    yearly_avg.to_csv(output_dir / f"{category}_avg_posts_race.csv", encoding="utf-8-sig")

    # 5. サマリーテーブル
    save_rankings_summary(df_raw, category, output_dir)

def save_combined_rankings(all_stats, output_dir, cat_names):
    """
    全ジャンルのランキングをまとめた比較表を作成する
    """
    # 指定された順序
    ordered_genres = ["overall", "game", "theater", "explanation", "kitchen", "onboard", "travel"]
    
    metrics = {
        "posts": ("投稿数", "投稿数"),
        "posters": ("投稿者数", "投稿者数")
    }
    
    combined_markdown = []
    
    for key, (label, _) in metrics.items():
        combined_data = {}
        for genre in ordered_genres:
            if genre not in all_stats:
                continue
            raw_stats = all_stats[genre]
            
            # 2025年のデータを使用
            df_2025_raw = raw_stats[raw_stats["year"] == 2025].copy()
            if df_2025_raw.empty:
                continue
            
            # 集集
            stats = df_2025_raw.groupby("character").agg({
                "contentId": "nunique",
                "userId": "nunique",
                "viewCounter": "sum"
            })
            medians = df_2025_raw.groupby("character")["viewCounter"].median()
            df_2025 = stats.join(medians.rename("median_views")).reset_index()
            
            df_2025.columns = ["character", "contentId", "userId", "viewCounter", "median_views"]
            df_2025["1人あたり平均投稿数"] = (df_2025["contentId"] / df_2025["userId"]).round(2)
            df_2025["平均再生数"] = (df_2025["viewCounter"] / df_2025["contentId"]).astype(int)
            
            # 各指標でソート
            if key == "posts":
                val_col = "contentId"
                sort_col = "contentId"
            else: # posters
                val_col = "userId"
                sort_col = "userId"
            
            df_sorted = df_2025.sort_values(sort_col, ascending=False).head(20).reset_index(drop=True)
            
            display_name = cat_names.get(genre, genre)
            entries = []
            for i, row in df_sorted.iterrows():
                char = row["character"]
                val = int(row[val_col])
                avg_v = int(row["平均再生数"])
                med_v = int(row["median_views"])
                
                if key == "posts":
                    avg_p = row["1人あたり平均投稿数"]
                    entries.append(f"{char} ({val} / {avg_p} / {avg_v} / {med_v})")
                else: # posters
                    entries.append(f"{char} ({val} / {avg_v} / {med_v})")
            
            # 20件に満たない場合は埋める
            while len(entries) < 20:
                entries.append("-")
            
            combined_data[display_name] = entries

        if not combined_data:
            continue

        df_combined = pd.DataFrame(combined_data)
        df_combined.index = range(1, 21)
        df_combined.index.name = "順位"
        
        combined_markdown.append(f"## 2025年 キャラクター{label}ランキング TOP 20 (ジャンル別比較)")
        combined_markdown.append(df_combined.reset_index().to_markdown(index=False))
        combined_markdown.append("")
        if key == "posts":
            combined_markdown.append("※ 形式: キャラクター名 (投稿数 / 1人あたり平均投稿数 / 平均再生数 / 再生数中央値)")
        else:
            combined_markdown.append("※ 形式: キャラクター名 (投稿者数 / 平均再生数 / 再生数中央値)")
        combined_markdown.append("\n")

    if combined_markdown:
        output_path = output_dir / "top_20_2025_combined_rankings.md"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("# 2025年 キャラクターランキング比較 (統合版)\n\n")
            f.write("\n".join(combined_markdown))
        print(f"Saved combined rankings to {output_path}")

    # 平均投稿数ランキングは単独で維持 (要望にないため)
    save_avg_posts_comparison(all_stats, output_dir, cat_names, ordered_genres)

def save_avg_posts_comparison(all_stats, output_dir, cat_names, ordered_genres):
    combined_data = {}
    for genre in ordered_genres:
        if genre not in all_stats:
            continue
        raw_stats = all_stats[genre]
        df_2025_raw = raw_stats[raw_stats["year"] == 2025].copy()
        if df_2025_raw.empty:
            continue
        
        df_2025 = df_2025_raw.groupby("character").agg({"contentId": "nunique", "userId": "nunique"}).reset_index()
        df_2025["1人あたり平均投稿数"] = (df_2025["contentId"] / df_2025["userId"]).round(2)
        df_sorted = df_2025.sort_values("contentId", ascending=False).head(20).reset_index(drop=True)
        
        display_name = cat_names.get(genre, genre)
        entries = [f"{row['character']} ({row['1人あたり平均投稿数']})" for i, row in df_sorted.iterrows()]
        while len(entries) < 20: entries.append("-")
        combined_data[display_name] = entries

    if combined_data:
        df_combined = pd.DataFrame(combined_data)
        df_combined.index = range(1, 21)
        output_path = output_dir / "top_20_2025_comparison_avg_posts.md"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("# 2025年 キャラクター1人あたり平均投稿数ランキング TOP 20 (ジャンル別比較)\n\n")
            f.write(df_combined.reset_index().rename(columns={"index": "順位"}).to_markdown(index=False))
        print(f"Saved avg posts comparison to {output_path}")

def main():
    target_categories = ["game", "onboard", "explanation", "kitchen", "theater", "travel", "fishing"]
    cat_names = {
        "overall": "全体",
        "software_talk": "全体",
        "game": "実況",
        "onboard": "車載",
        "explanation": "解説",
        "kitchen": "キッチン",
        "theater": "劇場",
        "travel": "旅行",
        "fishing": "釣行記"
    }
    
    output_dir = Path("results/history")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    character_names = load_characters()
    
    # 日本語フォント設定
    sns.set_style("whitegrid")
    try:
        import matplotlib_fontja
        matplotlib_fontja.japanize()
    except:
        import platform
        if platform.system() == "Windows":
            plt.rcParams['font.family'] = ['Meiryo', 'Yu Gothic', 'MS Gothic']

    all_genre_stats = {}

    # 1. 全体データの処理
    print("Processing overall data (software_talk)...")
    df_overall_raw = process_genre("software_talk", character_names)
    if not df_overall_raw.empty:
        # ノイズ除去
        df_overall_raw = df_overall_raw[~((df_overall_raw["character"] == "東北イタコ") & (df_overall_raw["year"] == 2013))]
        generate_all_rankings(df_overall_raw, "overall", output_dir, "全体")
        all_genre_stats["overall"] = df_overall_raw

    # 2. ジャンル別データの処理
    for genre in target_categories:
        df_genre = process_genre(genre, character_names)
        if df_genre.empty:
            continue
        generate_all_rankings(df_genre, genre, output_dir, cat_names.get(genre, genre))
        all_genre_stats[genre] = df_genre

    # 3. 比較表の作成
    save_combined_rankings(all_genre_stats, output_dir, cat_names)

    print("Done. Check results/history/")


if __name__ == "__main__":
    main()
