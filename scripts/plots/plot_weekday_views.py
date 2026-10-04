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

def generate_weekday_plot(df, suptitle, output_path):
    df = df.copy()
    df['weekday_num'] = df['startTime'].dt.weekday
    
    grouped = df.groupby('weekday_num').agg(
        video_count=('viewCounter', 'count'),
        total_views=('viewCounter', 'sum'),
        mean_views=('viewCounter', 'mean'),
        median_views=('viewCounter', 'median')
    ).reset_index()
    
    weekday_labels = ['月曜日', '火曜日', '水曜日', '木曜日', '金曜日', '土曜日', '日曜日']
    grouped = grouped.set_index('weekday_num').reindex(range(7)).fillna(0).reset_index()
    grouped['weekday_name'] = weekday_labels
    
    sns.set_theme(style="whitegrid", rc={"font.family": plt.rcParams['font.family']})
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    colors = ["#8fa0b5", "#8fa0b5", "#8fa0b5", "#8fa0b5", "#8fa0b5", "#2b6cb0", "#c53030"]
    
    # 1. 投稿動画数 (本)
    ax1 = axes[0, 0]
    sns.barplot(x='weekday_name', y='video_count', data=grouped, palette=colors, hue='weekday_name', legend=False, ax=ax1)
    ax1.set_title('投稿動画数', fontsize=16, pad=10)
    ax1.set_xlabel('投稿曜日', fontsize=12)
    ax1.set_ylabel('動画数 (本)', fontsize=12)
    for p in ax1.patches:
        height = p.get_height()
        ax1.annotate(f'{height:,.0f}本', (p.get_x() + p.get_width() / 2., height), ha='center', va='bottom', fontsize=11, fontweight='bold')
                     
    # 2. 総再生数 (万回)
    ax2 = axes[0, 1]
    grouped['total_views_man'] = grouped['total_views'] / 10000.0
    sns.barplot(x='weekday_name', y='total_views_man', data=grouped, palette=colors, hue='weekday_name', legend=False, ax=ax2)
    ax2.set_title('総再生数 (合計)', fontsize=16, pad=10)
    ax2.set_xlabel('投稿曜日', fontsize=12)
    ax2.set_ylabel('総再生数 (万回)', fontsize=12)
    for p in ax2.patches:
        height = p.get_height()
        ax2.annotate(f'{height:,.1f}万回', (p.get_x() + p.get_width() / 2., height), ha='center', va='bottom', fontsize=11, fontweight='bold')
                     
    # 3. 平均再生数 (回)
    ax3 = axes[1, 0]
    sns.barplot(x='weekday_name', y='mean_views', data=grouped, palette=colors, hue='weekday_name', legend=False, ax=ax3)
    ax3.set_title('平均再生数', fontsize=16, pad=10)
    ax3.set_xlabel('投稿曜日', fontsize=12)
    ax3.set_ylabel('平均再生数 (回)', fontsize=12)
    for p in ax3.patches:
        height = p.get_height()
        ax3.annotate(f'{height:,.0f}回', (p.get_x() + p.get_width() / 2., height), ha='center', va='bottom', fontsize=11, fontweight='bold')
                     
    # 4. 中央値再生数 (回)
    ax4 = axes[1, 1]
    sns.barplot(x='weekday_name', y='median_views', data=grouped, palette=colors, hue='weekday_name', legend=False, ax=ax4)
    ax4.set_title('中央値再生数', fontsize=16, pad=10)
    ax4.set_xlabel('投稿曜日', fontsize=12)
    ax4.set_ylabel('中央値再生数 (回)', fontsize=12)
    for p in ax4.patches:
        height = p.get_height()
        ax4.annotate(f'{height:,.0f}回', (p.get_x() + p.get_width() / 2., height), ha='center', va='bottom', fontsize=11, fontweight='bold')

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
    generate_weekday_plot(
        filtered_df,
        '車載カテゴリ 投稿曜日別の再生数・動画投稿数分析 (2025年/外れ値除外あり)\n(外れ値ユーザー 980198, 130380191 除外後)',
        'results/onboard/weekday_views_analysis.png'
    )
    
    # 2. 外れ値除外なしのプロット
    generate_weekday_plot(
        df,
        '車載カテゴリ 投稿曜日別の再生数・動画投稿数分析 (2025年/外れ値除外なし)',
        'results/onboard/weekday_views_analysis_with_outliers.png'
    )

if __name__ == "__main__":
    main()
