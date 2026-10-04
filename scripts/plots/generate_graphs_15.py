import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# ---------------------------------------------------------
# フォント・スタイル設定 (generate_graphs.py スタイル準拠)
# ---------------------------------------------------------
plt.rcParams['font.family'] = ['IBM Plex Sans JP', 'BIZ UDGothic', 'Yu Gothic', 'Meiryo', 'MS Gothic', 'sans-serif']
plt.rcParams['font.weight'] = 'bold'
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['axes.titleweight'] = 'bold'

plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = 'white'
plt.rcParams['text.color'] = '#333333'
plt.rcParams['axes.labelcolor'] = '#333333'
plt.rcParams['xtick.color'] = '#333333'
plt.rcParams['ytick.color'] = '#333333'
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['figure.dpi'] = 150

sns.set_theme(style="whitegrid", rc={
    "font.family": plt.rcParams['font.family'],
    "font.weight": "bold",
    "axes.labelweight": "bold",
    "axes.titleweight": "bold",
    "xtick.labelsize": 16,
    "ytick.labelsize": 16
})

OUTPUT_DIR = "D:/動画投稿/台本まとめ/graphs_15"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def save_fig(name):
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, f"{name}.png")
    plt.savefig(path, facecolor='white', edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")

# =========================================================
# 1. 彩澄りりせ 年別動画投稿数の推移 (2026年着地予測)
# =========================================================
def generate_graph_1():
    years = ['2022年', '2023年', '2024年', '2025年', '2026年実績\n(8/15時点)', '2026年予測\n(年間換算)']
    values = [19, 511, 551, 956, 894, 1443]
    colors = ['#667799', '#667799', '#667799', '#667799', '#95a5a6', '#e74c3c']

    # --- バージョン1: 予測値なし（2026実績まで、配置は完全一致） ---
    fig1, ax1 = plt.subplots(figsize=(14, 8))
    fig1.subplots_adjust(left=0.08, right=0.96, top=0.88, bottom=0.12)
    
    # 6本目を透明で描画して座標を固定
    bars1 = ax1.bar(years, values, color=[*colors[:5], 'none'], width=0.62, edgecolor='none')
    
    for i, (bar, val) in enumerate(zip(bars1, values)):
        if i == 5:  # 2026予測 (透明)
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 25,
                     f"{val:,}本", ha='center', va='bottom',
                     color=(0,0,0,0), fontsize=16, fontweight='bold')
        elif i == 4:  # 2026実績
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 25,
                     f"{val:,}本", ha='center', va='bottom',
                     color='#555555', fontsize=15, fontweight='bold')
        else:
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 25,
                     f"{val:,}本", ha='center', va='bottom',
                     color='#333333', fontsize=15, fontweight='bold')

    ax1.set_title('彩澄りりせ 年別動画投稿数の推移', fontsize=22, pad=25)
    ax1.set_ylabel('投稿本数 (本)', fontsize=18)
    ax1.set_ylim(0, 1650)
    ax1.tick_params(axis='x', labelsize=16)
    ax1.tick_params(axis='y', labelsize=16)
    
    # 6番目のX軸ラベルを透明にする
    xticks = ax1.get_xticklabels()
    xticks[5].set_color((0,0,0,0))
    
    path1 = os.path.join(OUTPUT_DIR, "1_ririse_posts_trend_actual_only.png")
    plt.savefig(path1, facecolor='white', edgecolor='none', dpi=150)
    plt.close()
    print(f"Saved: {path1}")

    # --- バージョン2: 予測値あり（完全版） ---
    fig2, ax2 = plt.subplots(figsize=(14, 8))
    fig2.subplots_adjust(left=0.08, right=0.96, top=0.88, bottom=0.12)
    
    bars2 = ax2.bar(years, values, color=colors, width=0.62, edgecolor='none')

    for i, (bar, val) in enumerate(zip(bars2, values)):
        if i == 5:  # 2026予測
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 25,
                     f"{val:,}本", ha='center', va='bottom',
                     color='#c0392b', fontsize=16, fontweight='bold')
        elif i == 4:  # 2026実績
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 25,
                     f"{val:,}本", ha='center', va='bottom',
                     color='#555555', fontsize=15, fontweight='bold')
        else:
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 25,
                     f"{val:,}本", ha='center', va='bottom',
                     color='#333333', fontsize=15, fontweight='bold')

    ax2.set_title('彩澄りりせ 年別動画投稿数の推移 (2026年着地予測)', fontsize=22, pad=25)
    ax2.set_ylabel('投稿本数 (本)', fontsize=18)
    ax2.set_ylim(0, 1650)
    ax2.tick_params(axis='x', labelsize=16)
    ax2.tick_params(axis='y', labelsize=16)
    
    path2 = os.path.join(OUTPUT_DIR, "1_ririse_posts_trend.png")
    plt.savefig(path2, facecolor='white', edgecolor='none', dpi=150)
    plt.close()
    print(f"Saved: {path2}")

# =========================================================
# 2. 年別 ユニーク投稿者数の推移
# =========================================================
def generate_graph_2():
    years = ['2022年', '2023年', '2024年', '2025年', '2026年\n(8/15時点)']
    values = [6, 107, 112, 198, 215]
    colors = ['#667799', '#667799', '#667799', '#667799', '#e74c3c']

    plt.figure(figsize=(14, 8))
    bars = plt.bar(years, values, color=colors, width=0.58, edgecolor='none')

    for i, (bar, val) in enumerate(zip(bars, values)):
        if i == 4:  # 2026年
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 4,
                     f"{val}人", ha='center', va='bottom',
                     color='#c0392b', fontsize=16, fontweight='bold')
        else:
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 4,
                     f"{val}人", ha='center', va='bottom',
                     color='#333333', fontsize=15, fontweight='bold')

    plt.title('年別 ユニーク投稿者数の推移', fontsize=22, pad=25)
    plt.ylabel('ユニーク投稿者数 (人)', fontsize=18)
    plt.ylim(0, 245)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    save_fig('2_ririse_creators_trend')

# =========================================================
# 3. 主要ジャンル別 投稿数の急成長 (2024年 vs 2025年 vs 2026年予測)
# =========================================================
def generate_graph_3():
    genres = ['ボカロ', '実況', '解説']
    vals_2024 = [0, 169, 14]
    vals_2025 = [188, 200, 9]
    vals_2026_proj = [381, 374, 31]

    x = np.arange(len(genres))
    width = 0.26

    plt.figure(figsize=(14, 8))
    b1 = plt.bar(x - width, vals_2024, width, label='2024年 実績', color='#bdc3c7')
    b2 = plt.bar(x, vals_2025, width, label='2025年 実績', color='#667799')
    b3_colors = ['#e74c3c', '#e74c3c', '#e74c3c']
    b3 = plt.bar(x + width, vals_2026_proj, width, label='2026年 着地予測', color=b3_colors)

    for bar in b1:
        h = bar.get_height()
        if h > 0:
            plt.text(bar.get_x() + bar.get_width()/2, h + 5, f"{int(h)}本", ha='center', va='bottom', fontsize=15, color='#555555', fontweight='bold')

    for bar in b2:
        h = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, h + 5, f"{int(h)}本", ha='center', va='bottom', fontsize=15, color='#333333', fontweight='bold')

    for bar in b3:
        h = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, h + 5, f"{int(h)}本", ha='center', va='bottom', fontsize=16, color='#c0392b', fontweight='bold')

    plt.title('主要ジャンル別 投稿数の急成長 (2024年 vs 2025年 vs 2026年予測)', fontsize=22, pad=25)
    plt.ylabel('投稿本数 (本)', fontsize=18)
    plt.xticks(x, genres, fontsize=18)
    plt.yticks(fontsize=16)
    plt.ylim(0, 440)
    plt.legend(fontsize=16, loc='upper right')
    save_fig('3_ririse_genre_growth')

# =========================================================
# 4. Synthesizer V参入によるクリエイター構造
# =========================================================
def generate_graph_4():
    labels = ['新規ボカロP (歌のみ)', '兼任クリエイター (トーク＋歌)']
    counts = [95, 37]
    colors = ['#e74c3c', '#3498db']

    fig, ax = plt.subplots(figsize=(14, 8))

    wedges, texts, autotexts = ax.pie(
        counts,
        labels=[f"{labels[0]}\n95人 (72.0%)", f"{labels[1]}\n37人 (28.0%)"],
        autopct='%1.1f%%',
        pctdistance=0.72,
        startangle=70,
        colors=colors,
        textprops=dict(color="#333333", fontsize=16, fontweight='bold'),
        wedgeprops=dict(width=0.45, edgecolor='white', linewidth=3),
        labeldistance=1.12
    )

    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(18)
        autotext.set_weight('bold')

    # Center text
    ax.text(0, 0.08, "総ボカロP数", ha='center', va='center', fontsize=18, fontweight='bold', color='#666666')
    ax.text(0, -0.08, "132人", ha='center', va='center', fontsize=28, fontweight='bold', color='#222222')

    plt.title('Synthesizer V参入によるクリエイター構造', fontsize=22, pad=25)
    
    # Message box positioned cleanly at the bottom
    fig.text(0.5, 0.03, '★ 新規参入が7割超！ Synthesizer Vが新規クリエイター流入の最大の起爆剤に',
             ha='center', va='bottom', fontsize=16, fontweight='bold', color='#c0392b',
             bbox=dict(boxstyle='round,pad=0.6', facecolor='#fdedec', edgecolor='#e74c3c', linewidth=1.5, alpha=0.95))

    save_fig('4_ririse_synv_creator_structure')

# =========================================================
# 5. ショート vs ロング 再生数・いいね数中央値の比較 (ボイロ系)
#    - 5_1_ririse_short_vs_long_views.png (単独フルサイズ: 再生数中央値)
#    - 5_2_ririse_short_vs_long_likes.png (単独フルサイズ: いいね数中央値)
#    - 5_ririse_short_vs_long_views_only.png (2分割版・再生数のみ、完全ピクセル一致)
#    - 5_ririse_short_vs_long.png (2分割版・完全版、完全ピクセル一致)
# =========================================================
def generate_graph_5():
    types = ['ロング動画', 'ショート動画']
    views_median = [229, 422]
    likes_median = [35, 29]

    # ---------------------------------------------------------
    # 【個別スライド版 1】再生数中央値（フルサイズ）
    # ---------------------------------------------------------
    plt.figure(figsize=(14, 8))
    bars = plt.bar(types, views_median, color=['#667799', '#e74c3c'], width=0.55)
    plt.title('ショート vs ロング 再生数中央値の比較 (ボイロ系)', fontsize=22, pad=25)
    plt.ylabel('再生数中央値 (回)', fontsize=18)
    plt.ylim(0, 490)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.text(bars[0].get_x() + bars[0].get_width()/2, views_median[0] + 10,
             f"{views_median[0]}回", ha='center', va='bottom', fontsize=18, fontweight='bold', color='#333333')
    plt.text(bars[1].get_x() + bars[1].get_width()/2, views_median[1] + 10,
             f"{views_median[1]}回", ha='center', va='bottom', fontsize=18, fontweight='bold', color='#c0392b')
    save_fig('5_1_ririse_short_vs_long_views')

    # ---------------------------------------------------------
    # 【個別スライド版 2】いいね数中央値（フルサイズ）
    # ---------------------------------------------------------
    plt.figure(figsize=(14, 8))
    bars = plt.bar(types, likes_median, color=['#2ecc71', '#95a5a6'], width=0.55)
    plt.title('ショート vs ロング いいね数中央値の比較 (ボイロ系)', fontsize=22, pad=25)
    plt.ylabel('いいね数中央値 (回)', fontsize=18)
    plt.ylim(0, 45)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.text(bars[0].get_x() + bars[0].get_width()/2, likes_median[0] + 1.0,
             f"{likes_median[0]}いいね", ha='center', va='bottom', fontsize=18, fontweight='bold', color='#27ae60')
    plt.text(bars[1].get_x() + bars[1].get_width()/2, likes_median[1] + 1.0,
             f"{likes_median[1]}いいね", ha='center', va='bottom', fontsize=18, fontweight='bold', color='#555555')
    save_fig('5_2_ririse_short_vs_long_likes')

    # ---------------------------------------------------------
    # 【2分割・完全ピクセル一致オーバーレイ版】
    # 固定マージン & 透明ダミー要素で厳密なピクセル完全一致を実現
    # ---------------------------------------------------------
    for is_views_only in [True, False]:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 8))
        fig.subplots_adjust(left=0.08, right=0.96, top=0.88, bottom=0.12, wspace=0.22)

        # Panel 1: 再生数
        b1 = ax1.bar(types, views_median, color=['#667799', '#e74c3c'], width=0.52)
        ax1.set_title('再生数中央値 (回)', fontsize=18, fontweight='bold', pad=15)
        ax1.set_ylabel('再生数中央値 (回)', fontsize=16)
        ax1.set_ylim(0, 490)
        ax1.tick_params(axis='x', labelsize=16)
        ax1.tick_params(axis='y', labelsize=15)
        ax1.text(b1[0].get_x() + b1[0].get_width()/2, views_median[0] + 10,
                 f"{views_median[0]}回", ha='center', va='bottom', fontsize=16, fontweight='bold', color='#333333')
        ax1.text(b1[1].get_x() + b1[1].get_width()/2, views_median[1] + 10,
                 f"{views_median[1]}回", ha='center', va='bottom', fontsize=16, fontweight='bold', color='#c0392b')

        # Panel 2: いいね数 (views_only時は透明描画でレイアウトと座標を完全固定)
        if is_views_only:
            b2 = ax2.bar(types, likes_median, color='none', edgecolor='none', width=0.52)
            t_color1, t_color2 = (0, 0, 0, 0), (0, 0, 0, 0)
        else:
            b2 = ax2.bar(types, likes_median, color=['#2ecc71', '#95a5a6'], width=0.52)
            t_color1, t_color2 = '#27ae60', '#555555'

        ax2.set_title('いいね数中央値 (回)', fontsize=18, fontweight='bold', pad=15)
        ax2.set_ylabel('いいね数中央値 (回)', fontsize=16)
        ax2.set_ylim(0, 45)
        ax2.tick_params(axis='x', labelsize=16)
        ax2.tick_params(axis='y', labelsize=15)
        ax2.text(b2[0].get_x() + b2[0].get_width()/2, likes_median[0] + 1.0,
                 f"{likes_median[0]}いいね", ha='center', va='bottom', fontsize=16, fontweight='bold', color=t_color1)
        ax2.text(b2[1].get_x() + b2[1].get_width()/2, likes_median[1] + 1.0,
                 f"{likes_median[1]}いいね", ha='center', va='bottom', fontsize=16, fontweight='bold', color=t_color2)

        fig.suptitle('ショート vs ロング 再生数・いいね数中央値の比較 (ボイロ系)', fontsize=22, fontweight='bold', y=0.97)

        # 保存時にbbox_inches='tight'を使わず固定キャンバスで保存
        name = '5_ririse_short_vs_long_views_only' if is_views_only else '5_ririse_short_vs_long'
        path = os.path.join(OUTPUT_DIR, f"{name}.png")
        plt.savefig(path, facecolor='white', edgecolor='none', dpi=150)
        plt.close()
        print(f"Saved (Exact Pixel Match): {path}")

# =========================================================
# 6. 共起キャラクターランキング TOP5 (全体2,931本中)
# =========================================================
def generate_graph_6():
    chars = ['彩澄しゅお', 'フリモメン', '桜乃そら', '小春六花', '宮舞モカ']
    counts = [1119, 229, 222, 195, 148]
    shares = ['38.2%', '7.8%', '7.6%', '6.7%', '5.0%']
    colors = ['#e74c3c', '#667799', '#667799', '#667799', '#667799']

    plt.figure(figsize=(14, 8))
    y_pos = np.arange(len(chars))

    bars = plt.barh(y_pos, counts, color=colors, height=0.58, edgecolor='none')

    for i, (bar, count, share) in enumerate(zip(bars, counts, shares)):
        w = bar.get_width()
        color = '#c0392b' if i == 0 else '#333333'
        plt.text(w + 25, bar.get_y() + bar.get_height()/2,
                 f"{count:,}本 ({share})",
                 ha='left', va='center', fontsize=15, fontweight='bold', color=color)

    plt.title('共起キャラクターランキング TOP5 (全体2,931本中)', fontsize=22, pad=25)
    plt.xlabel('共起動画数 (本)', fontsize=18)
    plt.yticks(y_pos, [f"{i+1}位: {c}" for i, c in enumerate(chars)], fontsize=16)
    plt.xticks(fontsize=16)
    plt.xlim(0, 1400)
    plt.gca().invert_yaxis()
    save_fig('6_ririse_cooccurrence_ranking')

# =========================================================
# 7. 主要ジャンル別「彩澄しゅお」関与率 (ボイロ系)
# =========================================================
def generate_graph_7():
    genres = ['実況', '劇場', 'キッチン', '解説', '旅行', 'ラジオ', '車載']
    rates = [47.1, 43.0, 37.5, 30.6, 29.0, 25.2, 14.9]
    details = ['360 / 765本', '317 / 737本', '6 / 16本', '22 / 72本', '108 / 372本', '29 / 115本', '34 / 228本']
    colors = ['#e74c3c', '#e74c3c', '#667799', '#667799', '#667799', '#667799', '#95a5a6']

    plt.figure(figsize=(14, 8))
    y_pos = np.arange(len(genres))

    bars = plt.barh(y_pos, rates, color=colors, height=0.6, edgecolor='none')

    for i, (bar, rate, det) in enumerate(zip(bars, rates, details)):
        w = bar.get_width()
        color = '#c0392b' if i in [0, 1] else '#333333'
        plt.text(w + 1.0, bar.get_y() + bar.get_height()/2,
                 f"{rate:.1f}%  ({det})",
                 ha='left', va='center', fontsize=14, fontweight='bold', color=color)

    plt.title('主要ジャンル別「彩澄しゅお」関与率 (ボイロ系)', fontsize=22, pad=25)
    plt.xlabel('彩澄しゅお 関与率 (%)', fontsize=18)
    plt.yticks(y_pos, genres, fontsize=16)
    plt.xticks(fontsize=16)
    plt.xlim(0, 58)
    plt.gca().invert_yaxis()
    save_fig('7_ririse_shuo_involvement_by_genre')

def main():
    print("Generating graphs based on specifications in 15_彩澄りりせ大解剖_構成案.md...")
    generate_graph_1()
    generate_graph_2()
    generate_graph_3()
    generate_graph_4()
    generate_graph_5()
    generate_graph_6()
    generate_graph_7()
    print("All graphs successfully generated in D:/動画投稿/台本まとめ/graphs_15/!")

if __name__ == '__main__':
    main()
