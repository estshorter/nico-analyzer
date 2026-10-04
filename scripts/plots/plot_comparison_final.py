"""
Processing Overview:
ニコニコ全体とボイロ界隈の年間投稿数および再生数の推移を比較する最終的なグラフを生成します。
全体データと界隈データの規模差が大きいため、2軸グラフ（Dual Axis）を使用し、
それぞれの実数スケールでの成長・変化の様子を1つの図で分かりやすく提示します。
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker
import matplotlib_fontja

def format_jp_large(x, pos):
    """Numbers to Japanese units (億, 万)"""
    if x >= 100000000:
        return f'{x/100000000:.1f}億'
    elif x >= 10000:
        return f'{x/10000:.0f}万'
    else:
        return f'{x:.0f}'

def plot_nico_vs_voiro_final():
    # Load data
    df = pd.read_csv('results/comparison/nico_vs_voiro.csv')

    # Set style
    sns.set_theme(style="whitegrid")
    matplotlib_fontja.japanize()

    fig, axes = plt.subplots(2, 1, figsize=(12, 12), sharex=True)

    # --- Plot 1: Videos Comparison (Dual Axis, Linear) ---
    ax1 = axes[0]
    # Left: Nico Total
    color1 = 'tab:blue'
    sns.lineplot(data=df, x='year', y='nico_total_videos', ax=ax1, label='ニコニコ全体 (左軸)', color=color1, marker='o', linewidth=2.5)
    ax1.set_ylabel('ニコニコ全体 投稿数', color=color1, fontsize=12, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.set_ylim(bottom=0)
    ax1.yaxis.set_major_formatter(ticker.FuncFormatter(format_jp_large))
    ax1.grid(True, which="major", ls="-", alpha=0.5)

    # Right: Voiro
    ax1_twin = ax1.twinx()
    color2 = 'tab:orange'
    sns.lineplot(data=df, x='year', y='voiro_videos', ax=ax1_twin, label='ボイロ界隈 (右軸)', color=color2, marker='s', linestyle='--', linewidth=2.5)
    ax1_twin.set_ylabel('ボイロ界隈 投稿数', color=color2, fontsize=12, fontweight='bold')
    ax1_twin.tick_params(axis='y', labelcolor=color2)
    ax1_twin.set_ylim(bottom=0)
    ax1_twin.yaxis.set_major_formatter(ticker.FuncFormatter(format_jp_large))
    ax1_twin.grid(False) # Hide right grid to avoid clutter

    ax1.set_title('年間投稿数の推移 (実数・2軸比較)', fontsize=14, pad=15)
    
    # Legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax1_twin.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper center', frameon=True)
    ax1_twin.get_legend().remove()


    # --- Plot 2: Views Comparison (Dual Axis, Linear) ---
    ax2 = axes[1]
    # Left: Nico Total
    color3 = 'tab:green'
    sns.lineplot(data=df, x='year', y='nico_total_views', ax=ax2, label='ニコニコ全体 (左軸)', color=color3, marker='o', linewidth=2.5)
    ax2.set_ylabel('ニコニコ全体 再生数', color=color3, fontsize=12, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor=color3)
    ax2.set_ylim(bottom=0)
    ax2.yaxis.set_major_formatter(ticker.FuncFormatter(format_jp_large))
    ax2.grid(True, which="major", ls="-", alpha=0.5)

    # Right: Voiro
    ax2_twin = ax2.twinx()
    color4 = 'tab:red'
    sns.lineplot(data=df, x='year', y='voiro_views', ax=ax2_twin, label='ボイロ界隈 (右軸)', color=color4, marker='s', linestyle='--', linewidth=2.5)
    ax2_twin.set_ylabel('ボイロ界隈 再生数', color=color4, fontsize=12, fontweight='bold')
    ax2_twin.tick_params(axis='y', labelcolor=color4)
    ax2_twin.set_ylim(bottom=0)
    ax2_twin.yaxis.set_major_formatter(ticker.FuncFormatter(format_jp_large))
    ax2_twin.grid(False)

    ax2.set_title('年間再生数の推移 (実数・2軸比較)', fontsize=14, pad=15)
    ax2.set_xlabel('年', fontsize=12)

    # Legends
    lines3, labels3 = ax2.get_legend_handles_labels()
    lines4, labels4 = ax2_twin.get_legend_handles_labels()
    ax2.legend(lines3 + lines4, labels3 + labels4, loc='upper center', frameon=True)
    ax2_twin.get_legend().remove()

    plt.tight_layout()
    output_path = 'results/comparison/nico_vs_voiro_final.png'
    plt.savefig(output_path, dpi=300)
    print(f"Final graph saved to {output_path}")

if __name__ == "__main__":
    plot_nico_vs_voiro_final()
