import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
import matplotlib_fontja
from pathlib import Path

def format_jp_large(x, pos):
    """数値を日本語の単位（億、万）に変換"""
    if abs(x) >= 100000000:
        return f'{x/100000000:.1f}億'
    elif abs(x) >= 10000:
        return f'{x/10000:.0f}万'
    else:
        return f'{x:.0f}'

def main():
    # Load data
    csv_path = Path('results/comparison/nico_vs_voiro.csv')
    df = pd.read_csv(csv_path)
    
    # Set style
    matplotlib_fontja.japanize()

    fig, ax = plt.subplots(figsize=(10, 6))
    twin1 = ax.twinx()

    x = df['year']
    y_posts = df['nico_total_videos']
    y_views = df['nico_total_views']

    # Bars for post count (C0)
    p1 = ax.bar(x, y_posts, color="C0", label="投稿数", alpha=0.6)
    # Line for view count (C1)
    (p2,) = twin1.plot(x, y_views, color="C1", marker="o", label="再生数")

    ax.set_xlabel("投稿年")
    ax.set_ylabel("投稿数")
    twin1.set_ylabel("再生数")
    ax.set_title("ニコニコ全体：年間投稿数と再生数の推移")

    # 軸のフォーマットを日本語単位に設定
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_jp_large))
    twin1.yaxis.set_major_formatter(ticker.FuncFormatter(format_jp_large))

    # Match analyzer.py's axis coloring
    ax.yaxis.label.set_color("C0")
    twin1.yaxis.label.set_color("C1")

    # Match legend
    ax.legend(handles=[p1, p2], loc='upper right')
    ax.set_axisbelow(True)
    ax.grid(False)
    twin1.grid(False)

    plt.tight_layout()
    
    output_path = Path('results/comparison/nico_total_annual-both.png')
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Saved {output_path}")

if __name__ == "__main__":
    main()
