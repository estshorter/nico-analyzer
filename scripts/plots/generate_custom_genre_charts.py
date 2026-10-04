import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# ジャンルごとの固定色定義
GENRE_COLORS = {
    'ボイロ': '#1f77b4',       # 青
    'VOCALOID': '#ff7f0e',    # オレンジ
    '公式アニメ': '#2ca02c',    # 緑
    '例のアレ': '#d62728',     # 赤
    'ゆっくり': '#9467bd',     # 紫
    '料理': '#8c564b',        # 茶
    '音MAD': '#e377c2',       # ピンク
    'biim': '#7f7f7f',        # グレー
    'ゲーム（肉声・字幕）': '#bcbd22', # 黄緑
    'その他': '#17becf'        # 水色
}

def setup_style():
    # フォント・スタイルの設定
    plt.rcParams['font.family'] = ['IBM Plex Sans JP', 'BIZ UDGothic', 'Yu Gothic', 'Meiryo', 'MS Gothic', 'sans-serif']
    plt.rcParams['font.weight'] = 'bold'
    plt.rcParams['axes.labelweight'] = 'bold'
    plt.rcParams['axes.titleweight'] = 'bold'

def save_chart(fig, filename):
    output_path = f'results/{filename}'
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Chart saved to {output_path}")

def get_colors(genres):
    # ジャンルリストに対応する色リストを返す。未定義の場合はグレー。
    return [GENRE_COLORS.get(g, '#cccccc') for g in genres]

def plot_views_share_bar_top5():
    data = {
        'genre': ['ボイロ', 'VOCALOID', '公式アニメ', '例のアレ', 'ゆっくり'],
        'share': [22.84, 14.48, 12.26, 11.66, 8.61]
    }
    df = pd.DataFrame(data).sort_values('share', ascending=True)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    colors = get_colors(df['genre'])
    bars = ax.barh(df['genre'], df['share'], color=colors, height=0.7)
    
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.5, bar.get_y() + bar.get_height()/2, f'{width:.1f}%',
                va='center', fontsize=24, weight='bold')
    
    ax.set_title('2025年 ニコニコ動画 ジャンル別再生数シェア', fontsize=28, pad=30)
    ax.set_xlabel('再生数シェア (%)', fontsize=20, labelpad=15)
    ax.tick_params(axis='y', labelsize=24)
    ax.set_xlim(0, max(df['share']) + 5)
    ax.xaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)
    for spine in ['top', 'right']: ax.spines[spine].set_visible(False)
    
    save_chart(fig, 'genre_views_share_bar_top5.png')

def plot_ranking_share_bar_top5():
    data = {
        'genre': ['ボイロ', 'ゆっくり', '公式アニメ', '例のアレ', 'biim'],
        'share': [46, 19, 12, 5, 5]
    }
    df = pd.DataFrame(data).sort_values('share', ascending=True)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    colors = get_colors(df['genre'])
    bars = ax.barh(df['genre'], df['share'], color=colors, height=0.7)
    
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 1, bar.get_y() + bar.get_height()/2, f'{width:.0f}%',
                va='center', fontsize=26, weight='bold')
    
    ax.set_title('24Hランキング上位100件のジャンル分布', fontsize=28, pad=30)
    ax.set_xlabel('シェア (%)', fontsize=20, labelpad=15)
    ax.tick_params(axis='y', labelsize=24)
    ax.set_xlim(0, max(df['share']) + 10)
    ax.xaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)
    for spine in ['top', 'right']: ax.spines[spine].set_visible(False)
    
    save_chart(fig, 'ranking_share_bar_top5.png')

def plot_likes_share_bar():
    data = {
        'genre': ['ボイロ', 'VOCALOID', 'ゆっくり', '例のアレ', '公式アニメ'],
        'share': [42.0, 11.35, 10.49, 6.96, 5.25]
    }
    df = pd.DataFrame(data).sort_values('share', ascending=True)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    colors = get_colors(df['genre'])
    bars = ax.barh(df['genre'], df['share'], color=colors, height=0.7)
    
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 1, bar.get_y() + bar.get_height()/2, f'{width:.1f}%',
                va='center', fontsize=26, weight='bold')
    
    ax.set_title('2025年 ニコニコ動画 ジャンル別いいね数シェア', fontsize=30, pad=30)
    ax.set_xlabel('いいね数シェア (%)', fontsize=22, labelpad=15)
    ax.tick_params(axis='y', labelsize=24)
    ax.set_xlim(0, max(df['share']) + 10)
    ax.xaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)
    for spine in ['top', 'right']: ax.spines[spine].set_visible(False)
    
    save_chart(fig, 'genre_likes_share_bar.png')

def plot_yearly_vs_ranking_drop():
    categories = ['VOCALOID', '例のアレ']
    yearly = [14.48, 11.66]
    ranking = [1, 5]
    
    x = np.arange(len(categories))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(12, 8))
    rects1 = ax.bar(x - width/2, yearly, width, label='2025年通年シェア', color='#66b3ff')
    rects2 = ax.bar(x + width/2, ranking, width, label='直近ランキングシェア', color='#ff9999')
    
    ax.set_ylabel('シェア (%)', fontsize=20)
    ax.set_title('通年再生数 vs ランキング分布の乖離', fontsize=28, pad=30)
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=22)
    ax.legend(fontsize=18)
    
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.1f}%',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=18, weight='bold')
    
    autolabel(rects1)
    autolabel(rects2)
    
    ax.set_ylim(0, 20)
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)
    for spine in ['top', 'right']: ax.spines[spine].set_visible(False)
    
    save_chart(fig, 'vocaloid_reonare_drop_comparison.png')

def plot_voiceroid_subgenre_comparison():
    labels = ['ゲーム実況', '劇場', '解説']
    yearly = [55.9, 20.1, 11.1]
    ranking = [41.3, 17.4, 19.6]
    
    x = np.arange(len(labels))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(14, 8))
    rects1 = ax.bar(x - width/2, yearly, width, label='2025年通年シェア', color='#66b3ff')
    rects2 = ax.bar(x + width/2, ranking, width, label='直近ランキングシェア', color='#ff9999')
    
    ax.set_ylabel('シェア (%)', fontsize=20)
    ax.set_title('ボイロ内サブジャンルの通年 vs ランキング比較', fontsize=28, pad=30)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=22)
    ax.legend(fontsize=18)
    
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.1f}%',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=18, weight='bold')
    
    autolabel(rects1)
    autolabel(rects2)
    
    ax.set_ylim(0, 65)
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)
    for spine in ['top', 'right']: ax.spines[spine].set_visible(False)
    
    save_chart(fig, 'voiceroid_subgenre_share_comparison.png')

if __name__ == "__main__":
    setup_style()
    plot_views_share_bar_top5()
    plot_ranking_share_bar_top5()
    plot_yearly_vs_ranking_drop()
    plot_voiceroid_subgenre_comparison()
    plot_likes_share_bar()
