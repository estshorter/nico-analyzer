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
実況、車載、キッチン、解説、劇場、旅行、釣りなどの各ジャンル間の統計情報を比較します。
ジャンルごとの年間投稿数、総再生数、および動画1本あたりの再生数中央値の推移を並列してグラフ化し、
ボイロ界隈における各ジャンルの規模感や勢いの違いを可視化します。
"""

import pickle
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib_fontja
import seaborn as sns
from pathlib import Path

from common_utils import filter_software_talk

def load_data(category):
    pickle_path = Path(f"results/{category}.pickle")
    if not pickle_path.exists():
        print(f"Warning: {pickle_path} not found.")
        return None
    
    with open(pickle_path, "rb") as f:
        recv = pickle.load(f)
    
    df = pd.json_normalize(recv["data"])
    df["startTime"] = pd.to_datetime(df["startTime"])
    df["year"] = df["startTime"].dt.year
    df["viewCounter"] = df["viewCounter"].astype(int)

    # ソフトウェアトークの場合、VOCALOID関連を除外（歌唱系が混じるため）
    if category == "software_talk":
        df = filter_software_talk(df)

    # 2025年まで（2026年は不完全なので除外するか、参考程度にする）
    df = df[df["year"] <= 2025]
    
    return df

def main():
    target_categories = ["software_talk", "game", "theater", "explanation", "kitchen", "onboard", "travel"]
    category_labels = {
        "onboard": "車載",
        "game": "実況",
        "kitchen": "キッチン",
        "explanation": "解説",
        "theater": "劇場",
        "software_talk": "全体",
        "travel": "旅行",
    }
    
    output_dir = Path("results/comparison")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Loading data...")
    data_frames = {}
    for cat in target_categories:
        df = load_data(cat)
        if df is not None:
            data_frames[cat] = df
            print(f"Loaded {cat}: {len(df)} records")

    

    # 集計
    stats_list = []
    
    for cat, df in data_frames.items():
        # 年ごとの集計
        yearly = df.groupby("year").agg(
            post_count=("contentId", "count"),
            total_views=("viewCounter", "sum"),
            median_views=("viewCounter", "median")
        ).reset_index()
        
        yearly["category"] = cat
        yearly["category_label"] = category_labels.get(cat, cat)
        stats_list.append(yearly)
    
    if not stats_list:
        print("No data to visualize.")
        return

    all_stats = pd.concat(stats_list, ignore_index=True)
    all_stats = all_stats[all_stats["year"] >= 2011] # 2011年以降に絞る
    all_stats = all_stats[all_stats["year"] <= 2025] # 2026年はデータが少ないため除外

    # CSV出力
    all_stats.to_csv(output_dir / "genre_comparison_yearly.csv", index=False, encoding="utf-8-sig")
    
    # 可視化設定
    sns.set_style("whitegrid")
    # 日本語フォント設定 (Seabornのスタイル設定後に実行)
    try:
        matplotlib_fontja.japanize()
    except:
        import platform
        if platform.system() == "Windows":
            plt.rcParams['font.family'] = ['Meiryo', 'Yu Gothic', 'MS Gothic']

    # 固定のカラーパレットを定義（プロット間で色を一致させるため）
    palette = {
        "全体": "tab:blue",
        "実況": "tab:orange",
        "劇場": "tab:green",
        "解説": "tab:red",
        "キッチン": "tab:purple",
        "車載": "tab:brown",
        "旅行": "tab:pink",
    }

    # 1. 投稿数推移
    plt.figure(figsize=(12, 7))
    sns.lineplot(data=all_stats, x="year", y="post_count", hue="category_label", palette=palette, marker="o", linewidth=2.5)
    plt.title("ジャンル別 年間投稿数推移 (2011-2025)", fontsize=22)
    plt.xlabel("年", fontsize=18)
    plt.ylabel("投稿数", fontsize=18)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.legend(title="ジャンル", fontsize=14, title_fontsize=14)
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig(output_dir / "comparison_post_count.png", dpi=300)
    plt.close()

    # 1c. 投稿数推移 (全体・実況除外)
    plt.figure(figsize=(12, 7))
    minor_stats = all_stats[~all_stats["category"].isin(["software_talk", "game"])]
    if not minor_stats.empty:
        sns.lineplot(data=minor_stats, x="year", y="post_count", hue="category_label", palette=palette, marker="o", linewidth=2.5)
        plt.title("ジャンル別 年間投稿数推移 (全体・実況除外)", fontsize=22)
        plt.xlabel("年", fontsize=18)
        plt.ylabel("投稿数", fontsize=18)
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)
        plt.legend(title="ジャンル", fontsize=14, title_fontsize=14)
        plt.grid(True, linestyle="--", alpha=0.7)
        plt.tight_layout()
        plt.savefig(output_dir / "comparison_post_count_minor.png", dpi=300)
    plt.close()

    # 1d. 投稿数推移 (小規模ジャンル)
    plt.figure(figsize=(12, 7))
    micro_stats = all_stats[~all_stats["category"].isin(["software_talk", "game", "theater","explanation"])]
    if not micro_stats.empty:
        sns.lineplot(data=micro_stats, x="year", y="post_count", hue="category_label", palette=palette, marker="o", linewidth=2.5)
        plt.title("ジャンル別 年間投稿数推移 (小規模ジャンル)", fontsize=22)
        plt.xlabel("年", fontsize=18)
        plt.ylabel("投稿数", fontsize=18)
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)
        plt.legend(title="ジャンル", fontsize=14, title_fontsize=14)
        plt.grid(True, linestyle="--", alpha=0.7)
        plt.tight_layout()
        plt.savefig(output_dir / "comparison_post_count_micro.png", dpi=300)
    plt.close()

    # 2. 総再生数推移
    plt.figure(figsize=(12, 7))
    sns.lineplot(data=all_stats, x="year", y="total_views", hue="category_label", palette=palette, marker="o", linewidth=2.5)
    plt.title("ジャンル別 年間総再生数推移 (2011-2025)", fontsize=22)
    plt.xlabel("年", fontsize=18)
    plt.ylabel("総再生数 (100万単位)", fontsize=18)
    
    import matplotlib.ticker as ticker
    def millions_formatter(x, pos):
        return f'{x/10**6:,.0f}'
    plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(millions_formatter))

    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.legend(title="ジャンル", fontsize=14, title_fontsize=14)
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig(output_dir / "comparison_total_views.png", dpi=300)
    plt.close()
    
    # 2c. 総再生数推移 (全体・実況除外)
    plt.figure(figsize=(12, 7))
    if not minor_stats.empty:
        sns.lineplot(data=minor_stats, x="year", y="total_views", hue="category_label", palette=palette, marker="o", linewidth=2.5)
        plt.title("ジャンル別 年間総再生数推移 (全体・実況除外)", fontsize=22)
        plt.xlabel("年", fontsize=18)
        plt.ylabel("総再生数 (100万単位)", fontsize=18)
        plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(millions_formatter))
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)
        plt.legend(title="ジャンル", fontsize=14, title_fontsize=14)
        plt.grid(True, linestyle="--", alpha=0.7)
        plt.tight_layout()
        plt.savefig(output_dir / "comparison_total_views_minor.png", dpi=300)
    plt.close()
    
    # 2d. 総再生数推移 (小規模ジャンル)
    plt.figure(figsize=(12, 7))
    micro_stats = all_stats[~all_stats["category"].isin(["software_talk", "game", "theater", "explanation"])]
    if not micro_stats.empty:
        sns.lineplot(data=micro_stats, x="year", y="total_views", hue="category_label", palette=palette, marker="o", linewidth=2.5)
        plt.title("ジャンル別 年間総再生数推移 (小規模ジャンル)", fontsize=22)
        plt.xlabel("年", fontsize=18)
        plt.ylabel("総再生数 (100万単位)", fontsize=18)
        plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(millions_formatter))
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)
        plt.ylim(top=14000000)
        plt.legend(title="ジャンル", fontsize=14, title_fontsize=14)
        plt.grid(True, linestyle="--", alpha=0.7)
        plt.tight_layout()
        plt.savefig(output_dir / "comparison_total_views_micro.png", dpi=300)
    plt.close()

    # 3. 再生数中央値推移
    plt.figure(figsize=(12, 7))
    sns.lineplot(data=all_stats, x="year", y="median_views", hue="category_label", palette=palette, marker="o", linewidth=2.5)
    plt.title("ジャンル別 再生数中央値推移 (2011-2025)", fontsize=22)
    plt.xlabel("年", fontsize=18)
    plt.ylabel("再生数中央値", fontsize=18)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.legend(title="ジャンル", fontsize=14, title_fontsize=14)
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.tight_layout()
    # plt.savefig(output_dir / "comparison_median_views.png", dpi=300)
    plt.close()

    print("Comparison graphs generated in results/comparison/")
    
    # 簡易レポート出力
    print("\n--- Summary (2025) ---")
    latest = all_stats[all_stats["year"] == 2025]
    print(latest[["category_label", "post_count", "total_views", "median_views"]])

if __name__ == "__main__":
    main()
