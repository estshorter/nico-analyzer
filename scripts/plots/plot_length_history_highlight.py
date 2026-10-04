import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
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

highlight_genres = ['実況', '劇場', 'キッチン']

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
    
    # 年ごとの中央値（秒）を計算
    median_per_year = df.groupby('year')['lengthSeconds'].median() / 60.0 # 分単位
    data_to_plot[label] = median_per_year

# グラフ作成
plt.figure(figsize=(12, 8))

# 指定された順序でプロット
target_order = ['実況', '車載', '旅行', '解説', 'キッチン', '劇場']
# Dark2からハイライト用の色を取得
base_colors = plt.cm.Dark2(np.arange(len(target_order)))

for i, label in enumerate(target_order):
    if label in data_to_plot:
        series = data_to_plot[label]
        
        if label in highlight_genres:
            color = base_colors[i]
            linewidth = 5.0
            markersize = 12
            alpha = 1.0
            zorder = 10
        else:
            color = '#d1d5db' # Gray
            linewidth = 2.5
            markersize = 8
            alpha = 0.6
            zorder = 1
            
        plt.plot(series.index, series.values, marker='o', label=label, color=color, 
                 linewidth=linewidth, markersize=markersize, alpha=alpha, zorder=zorder)

plt.title('ボイロ動画 ジャンル別動画時間の中央値 推移 (2020-2025)', pad=25, fontsize=24, fontweight='bold')
plt.xlabel('投稿年', labelpad=15, fontsize=20, fontweight='bold')
plt.ylabel('再生時間（分）', labelpad=15, fontsize=20, fontweight='bold')

plt.grid(True, which='both', linestyle='--', alpha=0.5)
# 凡例を外側に配置
plt.legend(loc='upper left', bbox_to_anchor=(1.02, 1), frameon=True, fontsize=16)

# X軸のメモリ調整
plt.xticks(range(2020, 2026))

# Y軸の範囲
plt.ylim(0, 15) 

# 右側に余白を確保するために調整
plt.subplots_adjust(right=0.82)

output_path = 'results/video_length_history_graph.png'
plt.savefig(output_path, bbox_inches='tight')
print(f'Graph saved to {output_path}')
