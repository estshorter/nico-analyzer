import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib_fontja
import numpy as np
from pathlib import Path

def format_jp_large(x, pos):
    """Numbers to Japanese units (億, 万)"""
    if abs(x) >= 100000000:
        return f'{x/100000000:.1f}億'
    elif abs(x) >= 10000:
        return f'{x/10000:.0f}万'
    else:
        return f'{x:.0f}'

def main():
    csv_path = Path('results/comparison/nico_vs_voiro.csv')
    df = pd.read_csv(csv_path)
    
    # Filter for 2020 onwards
    df_filtered = df[df['year'] >= 2020].copy()
    
    # Set style
    matplotlib_fontja.japanize()

    # --- 1. Nico Total Views ---
    fig1, ax1 = plt.subplots(figsize=(10, 7))
    years = df_filtered['year'].astype(str).tolist()
    x = np.arange(len(years))

    # Highlight 2023 and 2025
    colors_nico = ['lightgray' if year not in [2023, 2025] else '#555555' for year in df_filtered['year']]
    bars_nico = ax1.bar(x, df_filtered['nico_total_views'], color=colors_nico)
    
    for i, bar in enumerate(bars_nico):
        height = bar.get_height()
        year = df_filtered['year'].iloc[i]
        color = '#222222' if year in [2023, 2025] else 'dimgray'
        weight = 'bold' if year in [2023, 2025] else 'normal'
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                format_jp_large(height, None), ha='center', va='bottom', fontsize=12, color=color, fontweight=weight)

    ax1.set_ylabel('再生数')
    ax1.set_title('ニコニコ全体：年間再生数の推移 (2020-2025)', fontsize=16)
    ax1.set_xticks(x)
    ax1.set_xticklabels(years, fontsize=14)
    ax1.set_ylim(0, df_filtered['nico_total_views'].max() * 1.15)
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(format_jp_large))
    ax1.set_axisbelow(True)
    ax1.grid(True, axis='y', linestyle='--', alpha=0.7)
    ax1.grid(False, axis='x')
    fig1.tight_layout()
    output_path1 = Path('results/comparison/nico_total_views_2020_2025.png')
    fig1.savefig(output_path1, dpi=300)
    print(f"Graph saved to {output_path1}")

    # --- 2. Voiro Total Posts ---
    fig2, ax2 = plt.subplots(figsize=(10, 7))
    # Highlight 2023 and 2025
    colors_voiro = ['#A0C4FF' if year not in [2023, 2025] else 'tab:blue' for year in df_filtered['year']]
    bars_voiro = ax2.bar(x, df_filtered['voiro_videos'], color=colors_voiro)
    
    for i, bar in enumerate(bars_voiro):
        height = bar.get_height()
        year = df_filtered['year'].iloc[i]
        color = 'darkblue' if year in [2023, 2025] else 'tab:blue'
        weight = 'bold' if year in [2023, 2025] else 'normal'
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height):,}', ha='center', va='bottom', fontsize=12, color=color, fontweight=weight)

    ax2.set_ylabel('投稿数')
    ax2.set_title('ボイロ全体：年間投稿数の推移 (2020-2025)', fontsize=16)
    ax2.set_xticks(x)
    ax2.set_xticklabels(years, fontsize=14)
    ax2.set_ylim(0, df_filtered['voiro_videos'].max() * 1.15)
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
    ax2.set_axisbelow(True)
    ax2.grid(True, axis='y', linestyle='--', alpha=0.7)
    ax2.grid(False, axis='x')
    fig2.tight_layout()
    output_path2 = Path('results/comparison/voiro_total_posts_2020_2025.png')
    fig2.savefig(output_path2, dpi=300)
    print(f"Graph saved to {output_path2}")

if __name__ == "__main__":
    main()
