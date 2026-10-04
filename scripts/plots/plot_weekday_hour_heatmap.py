import pickle
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# フォント設定
plt.rcParams['font.family'] = ['IBM Plex Sans JP', 'BIZ UDGothic', 'Yu Gothic', 'Meiryo', 'MS Gothic', 'sans-serif']
plt.rcParams['font.weight'] = 'bold'
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['axes.titleweight'] = 'bold'

def generate_heatmap_plot(df, suptitle, prefix_path):
    df = df.copy()
    
    # 曜日の取得 (0=月曜日, 6=日曜日)
    df['weekday_num'] = df['startTime'].dt.weekday
    weekday_labels = ['月曜日', '火曜日', '水曜日', '木曜日', '金曜日', '土曜日', '日曜日']
    
    # 時間帯ビン (3時間ごと: 0, 3, 6, 9, 12, 15, 18, 21)
    df['time_bin'] = (df['startTime'].dt.hour // 3) * 3
    bin_labels = {
        0: '00:00-03:00',
        3: '03:00-06:00',
        6: '06:00-09:00',
        9: '09:00-12:00',
        12: '12:00-15:00',
        15: '15:00-18:00',
        18: '18:00-21:00',
        21: '21:00-24:00'
    }
    df['time_label'] = df['time_bin'].map(bin_labels)
    time_label_order = [bin_labels[h] for h in [0, 3, 6, 9, 12, 15, 18, 21]]
    
    # ピボットテーブルの作成用に関数定義
    def get_pivot(metric, aggfunc):
        pivot = df.pivot_table(
            values=metric,
            index='weekday_num',
            columns='time_label',
            aggfunc=aggfunc,
            fill_value=0
        )
        # 曜日を0〜6に再配置して日本語ラベルに変更
        pivot = pivot.reindex(index=range(7), columns=time_label_order, fill_value=0)
        pivot.index = weekday_labels
        return pivot

    pivot_count = get_pivot('viewCounter', 'count')
    pivot_total = get_pivot('viewCounter', 'sum') / 10000.0 # 万回単位
    pivot_mean = get_pivot('viewCounter', 'mean')
    pivot_median = get_pivot('viewCounter', 'median')
    
    # プロットのスタイル設定
    sns.set_theme(style="whitegrid", rc={"font.family": plt.rcParams['font.family']})
    fig, axes = plt.subplots(2, 2, figsize=(20, 14))
    
    # 1. 投稿動画数 (本)
    ax1 = axes[0, 0]
    sns.heatmap(pivot_count, annot=True, fmt=',.0f', cmap='flare', cbar_kws={'label': '動画数 (本)'}, ax=ax1, annot_kws={'weight': 'bold', 'size': 10})
    ax1.set_title('投稿動画数 (曜日×時間帯)', fontsize=16, pad=10)
    ax1.set_xlabel('投稿時間帯', fontsize=12)
    ax1.set_ylabel('投稿曜日', fontsize=12)
    
    # 2. 総再生数 (万回)
    ax2 = axes[0, 1]
    sns.heatmap(pivot_total, annot=True, fmt=',.1f', cmap='crest', cbar_kws={'label': '総再生数 (万回)'}, ax=ax2, annot_kws={'weight': 'bold', 'size': 10})
    ax2.set_title('総再生数 (合計・万回) (曜日×時間帯)', fontsize=16, pad=10)
    ax2.set_xlabel('投稿時間帯', fontsize=12)
    ax2.set_ylabel('投稿曜日', fontsize=12)
    
    # 3. 平均再生数 (回)
    ax3 = axes[1, 0]
    sns.heatmap(pivot_mean, annot=True, fmt=',.0f', cmap='mako', cbar_kws={'label': '平均再生数 (回)'}, ax=ax3, annot_kws={'weight': 'bold', 'size': 10})
    ax3.set_title('平均再生数 (曜日×時間帯)', fontsize=16, pad=10)
    ax3.set_xlabel('投稿時間帯', fontsize=12)
    ax3.set_ylabel('投稿曜日', fontsize=12)
    
    # 4. 中央値再生数 (回)
    ax4 = axes[1, 1]
    sns.heatmap(pivot_median, annot=True, fmt=',.0f', cmap='viridis', cbar_kws={'label': '中央値再生数 (回)'}, ax=ax4, annot_kws={'weight': 'bold', 'size': 10})
    ax4.set_title('中央値再生数 (曜日×時間帯)', fontsize=16, pad=10)
    ax4.set_xlabel('投稿時間帯', fontsize=12)
    ax4.set_ylabel('投稿曜日', fontsize=12)

    plt.suptitle(suptitle, fontsize=22, y=0.98, fontweight='bold')
    plt.tight_layout()
    
    os.makedirs(os.path.dirname(prefix_path), exist_ok=True)
    output_path = f"{prefix_path}.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Heatmap saved to {output_path}")

def main():
    print("Loading data...")
    pickle_path = 'results/onboard.pickle'
    if not os.path.exists(pickle_path):
        print(f"Error: {pickle_path} not found.")
        return

    with open(pickle_path, 'rb') as f:
        data = pickle.load(f)
    
    df = pd.DataFrame(data['data'])
    df['startTime'] = pd.to_datetime(df['startTime'])
    df = df[df['startTime'].dt.year == 2025].copy()
    
    # ユーザーID除外処理用のカラム準備
    df['userId_int'] = df['userId'].fillna(0).astype(int)
    exclude_users = [980198, 130380191]
    filtered_df = df[~df['userId_int'].isin(exclude_users)].copy()
    
    # 1. 外れ値除外ありのヒートマップ
    generate_heatmap_plot(
        filtered_df,
        '車載カテゴリ 投稿曜日×時間帯別の再生数・投稿動画数分析 (2025年/外れ値除外あり)\n(外れ値ユーザー 980198, 130380191 除外後)',
        'results/onboard/weekday_hour_heatmap'
    )
    
    # 2. 外れ値除外なしのヒートマップ
    generate_heatmap_plot(
        df,
        '車載カテゴリ 投稿曜日×時間帯別の再生数・投稿動画数分析 (2025年/外れ値除外なし)',
        'results/onboard/weekday_hour_heatmap_with_outliers'
    )

if __name__ == "__main__":
    main()
