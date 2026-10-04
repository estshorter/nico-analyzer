import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# フォント設定
plt.rcParams['font.family'] = ['IBM Plex Sans JP', 'BIZ UDGothic', 'Yu Gothic', 'Meiryo', 'MS Gothic', 'sans-serif']
plt.rcParams['font.weight'] = 'bold'
plt.rcParams['font.size'] = 16
plt.rcParams['axes.titlesize'] = 22
plt.rcParams['axes.labelsize'] = 18
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['legend.fontsize'] = 16
plt.rcParams['xtick.labelsize'] = 14
plt.rcParams['ytick.labelsize'] = 14
plt.rcParams['figure.dpi'] = 200

# データ読み込み
file_path = 'results/explanation.pickle'
if not os.path.exists(file_path):
    print(f'Error: {file_path} not found.')
    exit(1)

print(f'Reading {file_path}...')
raw_data = pd.read_pickle(file_path)
df = pd.DataFrame(raw_data['data'])

# 日付変換
df['startTime'] = pd.to_datetime(df['startTime'])
df['year'] = df['startTime'].dt.year
df = df[(df['year'] >= 2020) & (df['year'] <= 2025)]

# --- 中央値（全体）の計算 ---
median_all = df.groupby('year')['lengthSeconds'].median() / 60.0

# --- 中央値（量産者除外）の計算 ---
# 年間投稿数を計算
user_counts = df.groupby(['year', 'userId']).size().reset_index(name='post_count')

# 各年の量産者を特定（年間100本以上）
mass_producers = user_counts[user_counts['post_count'] >= 100]

# 除外後のデータを準備
def filter_mass_producers(row):
    year = row['year']
    user = row['userId']
    # その年の量産者リストにいるかチェック
    is_mass = ((mass_producers['year'] == year) & (mass_producers['userId'] == user)).any()
    return not is_mass

# 高速化のためマージを使用
df_with_counts = df.merge(user_counts, on=['year', 'userId'], how='left')
df_filtered = df_with_counts[df_with_counts['post_count'] < 100]

median_filtered = df_filtered.groupby('year')['lengthSeconds'].median() / 60.0

# --- グラフ作成 ---
plt.figure(figsize=(12, 7))

# 全体データ（幻）
plt.plot(median_all.index, median_all.values, marker='o', label='生データ', 
         color='#95a5a6', linewidth=4, markersize=10, linestyle='--')

# 100本未満（実体） - こちらを強調
plt.plot(median_filtered.index, median_filtered.values, marker='s', label='修正後', 
         color='#3498db', linewidth=6, markersize=12)

plt.title('ボイロ解説：動画時間の中央値推移（補正前後の比較）', pad=25)
plt.xlabel('投稿年', labelpad=10)
plt.ylabel('再生時間（分）', labelpad=10)

plt.grid(True, which='both', linestyle='--', alpha=0.5)
plt.legend(loc='upper right', frameon=True)

plt.xticks(range(2020, 2026))
# plt.ylim(0, 10)

output_path = 'results/explanation_length_correction.png'
plt.savefig(output_path, bbox_inches='tight')
print(f'Graph saved to {output_path}')

# 数値の確認用出力
print("\n--- 中央値比較 (分) ---")
comparison = pd.DataFrame({
    '全体(幻)': median_all,
    '補正後(実体)': median_filtered,
    '差分': median_filtered - median_all
})
print(comparison)
