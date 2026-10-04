# /// script
# dependencies = [
#   "matplotlib",
#   "matplotlib-fontja",
#   "pandas",
# ]
# ///

import matplotlib.pyplot as plt
import pandas as pd
import os
import matplotlib_fontja

def generate_bar_chart():
    # フォント・スタイルの設定
    plt.rcParams['font.family'] = ['IBM Plex Sans JP', 'BIZ UDGothic', 'Yu Gothic', 'Meiryo', 'MS Gothic', 'sans-serif']
    plt.rcParams['font.weight'] = 'bold'
    plt.rcParams['axes.labelweight'] = 'bold'
    plt.rcParams['axes.titleweight'] = 'bold'

    # Data (Excluding 'Others' as requested)
    data = {
        'genre': ['ボイロ', 'ボカロ', '公式アニメ', '例のアレ'],
        'views_share': [23.08, 14.48, 13.12, 11.54]
    }
    
    df = pd.DataFrame(data)
    # Sort by views_share for better bar chart presentation
    df = df.sort_values('views_share', ascending=True)
    
    # Plot settings
    fig, ax = plt.subplots(figsize=(12, 8))
    
    colors = ['#ffcc99', '#99ff99', '#66b3ff', '#ff9999'] # Adjusted to match order after sort
    
    # 横棒グラフの作成
    bars = ax.barh(df['genre'], df['views_share'], color=colors, height=0.7)
    
    # 数値ラベルの追加 (棒の先端)
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.5, bar.get_y() + bar.get_height()/2, 
                f'{width:.1f}%', 
                va='center', fontsize=28, weight='bold')

    # 各種ラベル・タイトルの設定 (スマホ向けに大きく)
    ax.set_title('2025年 ニコニコ動画 ジャンル別再生数シェア', fontsize=32, pad=30, weight='bold')
    ax.set_xlabel('再生数シェア (%)', fontsize=24, labelpad=20)
    ax.tick_params(axis='y', labelsize=26)
    ax.tick_params(axis='x', labelsize=20)
    
    # X軸の範囲調整 (数値ラベル用の余白)
    ax.set_xlim(0, max(df['views_share']) + 5)
    
    # グリッド（垂直方向）の追加
    ax.xaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)

    # 枠線の調整
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    
    # Save the chart
    output_path = 'results/genre_share_bar_2025.png'
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    generate_bar_chart()
