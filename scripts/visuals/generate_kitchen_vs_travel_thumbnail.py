import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os

# Windows環境用の日本語フォント設定 (メイリオ)
plt.rcParams['font.family'] = 'Meiryo'

# データの定義
categories = ['実況', '車載', 'キッチン']
values = [303, 574, 1279]
colors = ['#95A5A6', '#4682B4', '#FF4500'] # 実況（グレー）、車載（青）、キッチン（赤橙）

# グラフの設定
fig, ax = plt.subplots(figsize=(12, 6)) # 横幅を8から12に広げて間隔を確保
bars = ax.bar(categories, values, color=colors, width=0.6) # 太さは0.6に維持

# 軸、枠線の設定
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['bottom'].set_visible(True)    # 底辺の線のみ表示
ax.spines['bottom'].set_color('#333333') # 線の色を濃いグレーに
ax.spines['bottom'].set_linewidth(5)     # 線の太さを強調
ax.get_yaxis().set_visible(False)
ax.get_xaxis().set_visible(False)

# 数値の表示を削除

# レイアウトの調整
plt.tight_layout()

# 出力先ディレクトリの確認と作成
os.makedirs('results', exist_ok=True)
output_path = 'results/kitchen_vs_travel_thumbnail.png'

# 画像の保存 (背景透過)
plt.savefig(output_path, transparent=True, bbox_inches='tight', dpi=300)
print(f"サムネイル画像を保存しました: {output_path}")
