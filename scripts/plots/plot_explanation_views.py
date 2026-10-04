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
    print(f"Weekday plot saved to {output_path}")
    return grouped

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
    print(f"Time plot saved to {output_path}")
    return grouped

def generate_heatmap_plot(df, suptitle, output_path):
    df = df.copy()
    df['weekday_num'] = df['startTime'].dt.weekday
    weekday_labels = ['月曜日', '火曜日', '水曜日', '木曜日', '金曜日', '土曜日', '日曜日']
    
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
    
    def get_pivot(metric, aggfunc):
        pivot = df.pivot_table(values=metric, index='weekday_num', columns='time_label', aggfunc=aggfunc, fill_value=0)
        pivot = pivot.reindex(index=range(7), columns=time_label_order, fill_value=0)
        pivot.index = weekday_labels
        return pivot

    pivot_count = get_pivot('viewCounter', 'count')
    pivot_total = get_pivot('viewCounter', 'sum') / 10000.0
    pivot_mean = get_pivot('viewCounter', 'mean')
    pivot_median = get_pivot('viewCounter', 'median')
    
    sns.set_theme(style="whitegrid", rc={"font.family": plt.rcParams['font.family']})
    fig, axes = plt.subplots(2, 2, figsize=(20, 14))
    
    sns.heatmap(pivot_count, annot=True, fmt=',.0f', cmap='flare', cbar_kws={'label': '動画数 (本)'}, ax=axes[0, 0], annot_kws={'weight': 'bold', 'size': 10})
    axes[0, 0].set_title('投稿動画数 (曜日×時間帯)', fontsize=16, pad=10)
    
    sns.heatmap(pivot_total, annot=True, fmt=',.1f', cmap='crest', cbar_kws={'label': '総再生数 (万回)'}, ax=axes[0, 1], annot_kws={'weight': 'bold', 'size': 10})
    axes[0, 1].set_title('総再生数 (合計・万回) (曜日×時間帯)', fontsize=16, pad=10)
    
    sns.heatmap(pivot_mean, annot=True, fmt=',.0f', cmap='mako', cbar_kws={'label': '平均再生数 (回)'}, ax=axes[1, 0], annot_kws={'weight': 'bold', 'size': 10})
    axes[1, 0].set_title('平均再生数 (曜日×時間帯)', fontsize=16, pad=10)
    
    sns.heatmap(pivot_median, annot=True, fmt=',.0f', cmap='viridis', cbar_kws={'label': '中央値再生数 (回)'}, ax=axes[1, 1], annot_kws={'weight': 'bold', 'size': 10})
    axes[1, 1].set_title('中央値再生数 (曜日×時間帯)', fontsize=16, pad=10)

    for ax in axes.flat:
        ax.set_xlabel('投稿時間帯', fontsize=12)
        ax.set_ylabel('投稿曜日', fontsize=12)

    plt.suptitle(suptitle, fontsize=22, y=0.98, fontweight='bold')
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Heatmap saved to {output_path}")
    return pivot_count, pivot_median

def main():
    print("Loading data...")
    pickle_path = 'results/explanation.pickle'
    if not os.path.exists(pickle_path):
        print(f"Error: {pickle_path} not found.")
        return

    with open(pickle_path, 'rb') as f:
        data = pickle.load(f)
    
    df = pd.DataFrame(data['data'] if isinstance(data, dict) and 'data' in data else data)
    df['startTime'] = pd.to_datetime(df['startTime'])
    
    # 2025年の動画に限定
    df = df[df['startTime'].dt.year == 2025].copy()
    print(f"Total videos in 2025 (Explanation): {len(df)}")
    
    # ユーザーIDを整数に変換して除外処理を行う（NaNは除外）
    df['userId_int'] = df['userId'].fillna(0).astype(int)
    
    # 外れ値ユーザーの除外
    exclude_users = [980198, 130380191]
    filtered_df = df[~df['userId_int'].isin(exclude_users)].copy()
    print(f"Filtered videos in 2025: {len(filtered_df)}")
    
    # 1. 曜日別プロット
    generate_weekday_plot(
        filtered_df,
        '解説カテゴリ 投稿曜日別の再生数・動画投稿数分析 (2025年)\n(外れ値ユーザー 980198, 130380191 除外後)',
        'results/explanation/weekday_views_analysis.png'
    )
    
    # 2. 時間帯別プロット
    generate_time_plot(
        filtered_df,
        '解説カテゴリ 投稿時間帯別の再生数・動画投稿数分析 (3時間毎) (2025年)\n(外れ値ユーザー 980198, 130380191 除外後)',
        'results/explanation/time_views_analysis.png'
    )
    
    # 3. 2Dヒートマップ
    p_count, p_median = generate_heatmap_plot(
        filtered_df,
        '解説カテゴリ 投稿曜日×時間帯別の再生数・投稿動画数分析 (2025年)\n(外れ値ユーザー 980198, 130380191 除外後)',
        'results/explanation/weekday_hour_heatmap.png'
    )
    
    # Find the peak median cell (excluding cells with very small sample size, say count < 20 to avoid noise)
    print("\n--- Details for Peak Finding ---")
    valid_medians = p_median[p_count >= 20]
    if not valid_medians.empty:
        max_med_idx = valid_medians.stack().idxmax()
        print(f"Peak median cell (count >= 20): {max_med_idx}, Value: {p_median.loc[max_med_idx]}, Count: {p_count.loc[max_med_idx]}")
    else:
        max_med_idx = p_median.stack().idxmax()
        print(f"Peak median cell (all): {max_med_idx}, Value: {p_median.loc[max_med_idx]}, Count: {p_count.loc[max_med_idx]}")
        
if __name__ == "__main__":
    main()
