import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# フォント設定：IBM Plex Sans JP を優先
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

data_2025 = {}

for key, label in genres.items():
    file_path = f'results/{key}.pickle'
    if not os.path.exists(file_path):
        continue
    
    raw_data = pd.read_pickle(file_path)
    df = pd.DataFrame(raw_data['data'])
    
    df['startTime'] = pd.to_datetime(df['startTime'])
    df['year'] = df['startTime'].dt.year
    
    # 2025年のデータのみ抽出して中央値を計算
    median_2025 = df[df['year'] == 2025]['lengthSeconds'].median() / 60.0
    data_2025[label] = median_2025

# 指定された順序でデータを並び替え（横棒グラフなので、上が「キッチン」になるように逆順にする）
target_order = ['キッチン', '車載', '劇場', '旅行', '解説', '実況']
plot_labels = []
plot_values = []
# target_orderの各要素に対応する色をDark2から取得
full_colors = plt.cm.Dark2(np.arange(len(target_order)))
plot_colors = []

# plt.barh は下から描画されるため、リストを反転させる
for i, label in enumerate(reversed(target_order)):
    if label in data_2025:
        plot_labels.append(label)
        plot_values.append(data_2025[label])
        # 元のtarget_orderでのインデックスに対応する色を取得
        orig_idx = len(target_order) - 1 - i
        plot_colors.append(full_colors[orig_idx])

# グラフ作成（横棒グラフ）
plt.figure(figsize=(12, 8))
bars = plt.barh(plot_labels, plot_values, color=plot_colors, edgecolor='black', linewidth=1.5)

# バーの右側に数値を表示
for bar in bars:
    width = bar.get_width()
    plt.text(width + 0.2, bar.get_y() + bar.get_height()/2,
             f'{width:.1f}分', va='center', fontsize=18, fontweight='bold')

plt.title('ジャンル別動画時間の中央値 (2025年)', pad=25, fontweight='bold')
plt.xlabel('再生時間（分）', labelpad=15, fontweight='bold')
plt.ylabel('ジャンル', labelpad=15, fontweight='bold')

plt.grid(axis='x', linestyle='--', alpha=0.7)
plt.xlim(0, max(plot_values) * 1.2) # 少し余裕を持たせる

output_path = 'results/video_length_2025_bar.png'
plt.savefig(output_path, bbox_inches='tight')
print(f'Graph saved to {output_path}')
