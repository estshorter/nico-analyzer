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

def generate_time_plot(df, suptitle, output_path):
    df = df.copy()
    df['time_bin'] = (df['startTime'].dt.hour // 3) * 3
    
    grouped = df.groupby('time_bin').agg(
        video_count=('viewCounter', 'count'),
        total_views=('viewCounter', 'sum'),
        mean_views=('viewCounter', 'mean'),
        median_views=('viewCounter', 'median')
    ).reset_index()
    
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
    grouped = grouped.set_index('time_bin').reindex([0, 3, 6, 9, 12, 15, 18, 21]).fillna(0).reset_index()
    grouped['time_label'] = grouped['time_bin'].map(bin_labels)
    
    sns.set_theme(style="whitegrid", rc={"font.family": plt.rcParams['font.family']})
    fig, axes = plt.subplots(2, 2, figsize=(18, 12))
    colors = ["#2e1065", "#1e3a8a", "#0369a1", "#ea580c", "#eab308", "#d97706", "#4f46e5", "#3b0764"]
    
    # 1. 投稿動画数 (本)
    ax1 = axes[0, 0]
    sns.barplot(x='time_label', y='video_count', data=grouped, palette=colors, hue='time_label', legend=False, ax=ax1)
    ax1.set_title('投稿動画数', fontsize=16, pad=10)
    ax1.set_xlabel('投稿時間帯', fontsize=12)
    ax1.set_ylabel('動画数 (本)', fontsize=12)
    ax1.tick_params(axis='x', rotation=15)
    for p in ax1.patches:
        height = p.get_height()
        ax1.annotate(f'{height:,.0f}本', (p.get_x() + p.get_width() / 2., height), ha='center', va='bottom', fontsize=10, fontweight='bold')
                     
    # 2. 総再生数 (万回)
    ax2 = axes[0, 1]
    grouped['total_views_man'] = grouped['total_views'] / 10000.0
    sns.barplot(x='time_label', y='total_views_man', data=grouped, palette=colors, hue='time_label', legend=False, ax=ax2)
    ax2.set_title('総再生数 (合計)', fontsize=16, pad=10)
    ax2.set_xlabel('投稿時間帯', fontsize=12)
    ax2.set_ylabel('総再生数 (万回)', fontsize=12)
    ax2.tick_params(axis='x', rotation=15)
    for p in ax2.patches:
        height = p.get_height()
        ax2.annotate(f'{height:,.1f}万回', (p.get_x() + p.get_width() / 2., height), ha='center', va='bottom', fontsize=10, fontweight='bold')
                     
    # 3. 平均再生数 (回)
    ax3 = axes[1, 0]
    sns.barplot(x='time_label', y='mean_views', data=grouped, palette=colors, hue='time_label', legend=False, ax=ax3)
    ax3.set_title('平均再生数', fontsize=16, pad=10)
    ax3.set_xlabel('投稿時間帯', fontsize=12)
    ax3.set_ylabel('平均再生数 (回)', fontsize=12)
    ax3.tick_params(axis='x', rotation=15)
    for p in ax3.patches:
        height = p.get_height()
        ax3.annotate(f'{height:,.0f}回', (p.get_x() + p.get_width() / 2., height), ha='center', va='bottom', fontsize=10, fontweight='bold')
                     
    # 4. 中央値再生数 (回)
    ax4 = axes[1, 1]
    sns.barplot(x='time_label', y='median_views', data=grouped, palette=colors, hue='time_label', legend=False, ax=ax4)
    ax4.set_title('中央値再生数', fontsize=16, pad=10)
    ax4.set_xlabel('投稿時間帯', fontsize=12)
    ax4.set_ylabel('中央値再生数 (回)', fontsize=12)
    ax4.tick_params(axis='x', rotation=15)
    for p in ax4.patches:
        height = p.get_height()
        ax4.annotate(f'{height:,.0f}回', (p.get_x() + p.get_width() / 2., height), ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.suptitle(suptitle, fontsize=20, y=0.98, fontweight='bold')
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Plot saved to {output_path}")
    return grouped

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
    
    # 1. 外れ値除外ありのプロット (通常版)
    generate_time_plot(
        filtered_df,
        '車載カテゴリ 投稿時間帯別の再生数・動画投稿数分析 (3時間毎) (2025年/外れ値除外あり)\n(外れ値ユーザー 980198, 130380191 除外後)',
        'results/onboard/time_views_analysis.png'
    )
    
    # 2. 外れ値除外なしのプロット
    generate_time_plot(
        df,
        '車載カテゴリ 投稿時間帯別の再生数・動画投稿数分析 (3時間毎) (2025年/外れ値除外なし)',
        'results/onboard/time_views_analysis_with_outliers.png'
    )

if __name__ == "__main__":
    main()
