# /// script
# dependencies = [
#   "matplotlib",
#   "matplotlib-fontja",
#   "pandas",
#   "numpy",
#   "seaborn",
# ]
# ///

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib_fontja
import numpy as np
import os

# フォント設定：IBM Plex Sans JP を優先（太字設定）
plt.rcParams['font.family'] = ['IBM Plex Sans JP', 'BIZ UDGothic', 'Yu Gothic', 'Meiryo', 'MS Gothic', 'sans-serif']
plt.rcParams['font.weight'] = 'bold'

plt.rcParams['font.size'] = 16
plt.rcParams['axes.titlesize'] = 24
plt.rcParams['axes.labelsize'] = 20
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['legend.fontsize'] = 16
plt.rcParams['xtick.labelsize'] = 16
plt.rcParams['ytick.labelsize'] = 16
plt.rcParams['figure.dpi'] = 200

genres = {
    'kitchen': 'キッチン',
    'onboard': '車載',
    'theater': '劇場',
    'game': '実況',
    'travel': '旅行',
    'explanation': '解説'
}

data_to_plot = {}

for key, label in genres.items():
    file_path = f'results/{key}.pickle'
    if not os.path.exists(file_path):
        print(f'Warning: {file_path} not found.')
        continue
    
    print(f'Reading {file_path}...')
    raw_data = pd.read_pickle(file_path)
    df = pd.DataFrame(raw_data['data'])
    
    # 日付変換とフィルタリング
    df['startTime'] = pd.to_datetime(df['startTime'])
    df['year'] = df['startTime'].dt.year
    df = df[df['year'] >= 2020]
    
    # 2026年は除外（2025年まで）
    df = df[df['year'] <= 2025]
    
    # viewCounterを数値に変換
    df['viewCounter'] = df['viewCounter'].astype(float)
    
    # 年ごとの再生数中央値を計算
    median_per_year = df.groupby('year')['viewCounter'].median()
    data_to_plot[label] = median_per_year

# グラフ作成
plt.figure(figsize=(14, 8))

# 指定された順序でプロット
target_order = ['実況', '車載', '旅行', '解説', 'キッチン', '劇場']
colors = plt.cm.Dark2(np.arange(len(target_order)))

max_val = 0
for i, label in enumerate(target_order):
    if label in data_to_plot:
        series = data_to_plot[label]
        # 線の太さとマーカーサイズも拡大
        plt.plot(series.index, series.values, marker='o', label=label, color=colors[i], linewidth=4.5, markersize=12)
        if not series.empty:
            max_val = max(max_val, series.max())

plt.title('ボイロ動画 ジャンル別再生数中央値の推移 (2020-2025)', pad=25, fontsize=24, fontweight='bold')
plt.xlabel('投稿年', labelpad=15, fontsize=20, fontweight='bold')
plt.ylabel('再生数中央値', labelpad=15, fontsize=20, fontweight='bold')

plt.grid(True, which='both', linestyle='--', alpha=0.5)
# 凡例を外側に配置
plt.legend(loc='upper left', bbox_to_anchor=(1.02, 1), frameon=True, fontsize=16)

# X軸のメモリ調整
plt.xticks(range(2020, 2026))

# Y軸の範囲 (中央値なので数千程度)
plt.ylim(0, max_val * 1.1)

# カンマ区切りのフォーマットを適用
from matplotlib.ticker import FuncFormatter
plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda x, p: format(int(x), ',')))

# 右側に余白を確保するために調整
plt.subplots_adjust(right=0.82)

output_path = 'results/video_view_history_graph.png'
plt.savefig(output_path, bbox_inches='tight')
print(f'Graph saved to {output_path}')
