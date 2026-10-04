# /// script
# dependencies = [
#   "matplotlib",
#   "matplotlib-fontja",
#   "pandas",
# ]
# ///

import pickle
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib_fontja

def main():
    # フォント・スタイルの設定 (plot_gini_history.py を参考)
    plt.rcParams['font.family'] = ['IBM Plex Sans JP', 'BIZ UDGothic', 'Yu Gothic', 'Meiryo', 'MS Gothic', 'sans-serif']
    plt.rcParams['font.weight'] = 'bold'
    plt.rcParams['font.size'] = 16
    plt.rcParams['axes.titlesize'] = 24
    plt.rcParams['axes.labelsize'] = 20
    plt.rcParams['axes.labelweight'] = 'bold'
    plt.rcParams['axes.titleweight'] = 'bold'
    plt.rcParams['figure.dpi'] = 200

    # データの読み込み
    pickle_path = Path("results/explanation.pickle")
    with open(pickle_path, "rb") as f:
        recv = pickle.load(f)
    df = pd.json_normalize(recv["data"])

    df["startTime"] = pd.to_datetime(df["startTime"])
    df["year"] = df["startTime"].dt.year
    df["lengthSeconds"] = df["lengthSeconds"].astype(int)
    df["viewCounter"] = df["viewCounter"].astype(float)

    # 2024年のデータに絞り込み
    df_2024 = df[df["year"] == 2024]
    
    # 0〜2分 (120秒) 以下の集計
    short_df = df_2024[df_2024["lengthSeconds"] <= 120]
    long_df = df_2024[df_2024["lengthSeconds"] > 120]

    # シェアの計算
    total_posts = len(df_2024)
    short_posts_share = (len(short_df) / total_posts) * 100
    long_posts_share = 100 - short_posts_share

    total_views = df_2024["viewCounter"].sum()
    short_views_share = (short_df["viewCounter"].sum() / total_views) * 100
    long_views_share = 100 - short_views_share

    # グラフの作成
    for hidden in [True, False]:
        fig, ax = plt.subplots(figsize=(10, 8))

        # Dark2の紫色 (colors[2]) を模倣した色
        # Dark2 color 2 is typically #7570b3
        short_color = "#7570b3"
        long_color = "#cccccc" # ライトグレー

        labels = ["投稿数シェア", "総再生数シェア"]
        current_short = [short_posts_share, short_views_share if not hidden else 0]
        current_long = [long_posts_share, long_views_share if not hidden else 0]

        # 積み上げ棒グラフ (下から 0-2m, 上に 2m+)
        ax.bar(labels, current_short, color=short_color, label="0〜2分動画", width=0.6)
        ax.bar(labels, current_long, bottom=current_short, color=long_color, label="2分超の動画", width=0.6)

        # 数値の印字 (0-2分動画の領域)
        for i, share in enumerate(current_short):
            if share > 0:
                ax.text(i, share / 2, f"{share:.1f}%", ha='center', va='center', color='white', fontweight='bold', fontsize=24)

        ax.set_ylabel("シェア (%)")
        ax.set_title("2024年 解説ジャンルにおける短尺動画の存在感\n(投稿数 vs 再生数)", pad=20)
        ax.set_ylim(0, 100)
        
        # 凡例
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

        plt.tight_layout()
        suffix = "_hidden" if hidden else ""
        output_path = Path(f"results/explanation_short_share_2024{suffix}.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Graph saved to {output_path}")

    print(f"0-2m Posts: {short_posts_share:.1f}%")
    print(f"0-2m Views: {short_views_share:.1f}%")

if __name__ == "__main__":
    main()
