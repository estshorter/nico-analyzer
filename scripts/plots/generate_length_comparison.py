import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os

# 日本語フォントの設定（NotoSansJPがルートにある場合）
font_path = "NotoSansJP-Regular.ttf"
try:
    if os.path.exists(font_path):
        fm.fontManager.addfont(font_path)
        plt.rcParams['font.family'] = fm.FontProperties(fname=font_path).get_name()
    else:
        plt.rcParams['font.family'] = ['Meiryo', 'Yu Gothic', 'sans-serif']
except RuntimeError:
    # Windowsのデフォルトフォント等へのフォールバック
    plt.rcParams['font.family'] = ['Meiryo', 'Yu Gothic', 'sans-serif']

# 2025年の中央値データ（秒換算）
# 車載動画：8分16秒 = 496秒
# キッチン動画：4分01秒 = 241秒
car_time = (8 * 60 + 16) / 60
kitchen_time = (4 * 60 + 1) / 60

# 図のサイズを少し大きくして、文字が収まりやすくする
fig, ax = plt.subplots(figsize=(12, 6))

y_pos = [1, 0]

# 車載動画のバー
car_color = '#4C72B0' # 落ち着いたブルー
ax.barh(y_pos[0], car_time, height=0.5, color=car_color)
ax.text(car_time / 2, y_pos[0], 'ボイロ車載動画 (中央値：8分16秒)', 
        ha='center', va='center', color='white', fontweight='bold', fontsize=20)

# キッチン動画のバー（2本）
kitchen_color = '#DD8452' # 温かみのあるオレンジ
# 1本目
ax.barh(y_pos[1], kitchen_time, height=0.5, color=kitchen_color, edgecolor='white', linewidth=2)
ax.text(kitchen_time / 2, y_pos[1], 'キッチン 1本目\n(4分01秒)', 
        ha='center', va='center', color='white', fontweight='bold', fontsize=20)

# 2本目
ax.barh(y_pos[1], kitchen_time, left=kitchen_time, height=0.5, color=kitchen_color, edgecolor='white', linewidth=2)
ax.text(kitchen_time + kitchen_time / 2, y_pos[1], 'キッチン 2本目\n(4分01秒)', 
        ha='center', va='center', color='white', fontweight='bold', fontsize=20)

# 軸とタイトルの設定
ax.set_yticks(y_pos)
ax.set_yticklabels(['車載動画', 'キッチン動画'], fontsize=20, fontweight='bold')
ax.set_xlabel('再生時間（分）', fontsize=16)
ax.set_xlim(0, max(car_time, kitchen_time * 2) + 1)
#ax.set_title('1回の視聴枠（約8分）における消化本数の違い\n～なぜキッチン動画は「回遊」されるのか～', 
#             fontsize=24, fontweight='bold', pad=20)

# 枠線を消してスッキリさせる
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.tick_params(axis='y', length=0) # y軸の目盛り線を消す

# 「スキマ時間（約8分）」の目安を示す縦線を引く
#ax.axvline(x=car_time, color='gray', linestyle='--', alpha=0.7)
#ax.text(car_time + 5, 0.5, '視聴者のスキマ時間\n（約8分）', color='gray', fontsize=18, va='center')

plt.tight_layout()

# 画像として保存
output_path = 'docs/comparison_video_length.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"画像を作成しました: {output_path}")
