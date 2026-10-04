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

    fig, ax = plt.subplots()
    twin1 = ax.twinx()

    x = df['year']
    y_posts = df['nico_total_videos']
    y_views = df['nico_total_views'] / 1e8  # 1億単位に変換

    # Bars for post count (C0)
    p1 = ax.bar(x, y_posts, color="C0", label="投稿数", alpha=0.6)
    # Line for view count (C1)
    (p2,) = twin1.plot(x, y_views, color="C1", marker="o", label="再生数")

    ax.set_xlabel("投稿年")
    ax.set_ylabel("投稿数")
    twin1.set_ylabel("再生数（億単位）")
    ax.set_title("ニコニコ全体：年間投稿数と再生数の推移")

    # 投稿数（左軸）のみ日本語単位を適用、再生数（右軸）は数値のみ
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_jp_large))
    # twin1 は数値そのまま（ラベルで単位を指定しているため）

    # Match analyzer.py's axis coloring
    ax.yaxis.label.set_color("C0")
    twin1.yaxis.get_label().set_color(p2.get_color())

    # 再生数のy軸の開始位置を調整 (0にする)
    twin1.set_ylim(bottom=0)

    # Match legend
    ax.legend(handles=[p1, p2])
    ax.set_axisbelow(True)
    ax.grid(axis='x', linestyle=":", alpha=0.6)

    plt.gcf().autofmt_xdate()
    
    output_path = Path('results/comparison/nico_total_annual-both.png')
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close("all")
    print(f"Saved {output_path}")

if __name__ == "__main__":
    main()
