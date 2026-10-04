import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

plt.rcParams['font.family'] = ['IBM Plex Sans JP', 'BIZ UDGothic', 'Yu Gothic', 'Meiryo', 'MS Gothic', 'sans-serif']
plt.rcParams['font.weight'] = 'bold'
plt.rcParams['font.size'] = 12
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['figure.dpi'] = 200

OUT_DIR = Path("results/simple_onboard")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def plot_daily_counts():
    df_daily = pd.read_csv(OUT_DIR / "daily_post_counts.csv")
    fig, ax = plt.subplots(figsize=(13, 6))
    
    years = [2023, 2024, 2025, 2026]
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    labels = [
        '2023年 (7/4 ~ 7/18)',
        '2024年 (8/19 ~ 9/2 ※延期開催)',
        '2025年 (7/8 ~ 7/22)',
        '2026年 (7/7 ~ 7/21)'
    ]
    
    for i, year in enumerate(years):
        sub = df_daily[df_daily['year'] == year].sort_values('day_num')
        if not sub.empty:
            ax.plot(sub['day_num'], sub['count'], marker='o', linewidth=2.5, markersize=7, label=labels[i], color=colors[i])
        
    ax.set_xlabel("開催日 (1日目 〜 15日目)", labelpad=10)
    ax.set_ylabel("投稿数 (本)", labelpad=10)
    ax.set_title("シンプル車載動画投稿祭 日別投稿数の推移 (2023-2026)", pad=15)
    ax.set_xticks(range(1, 16))
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(frameon=True, facecolor='white', framealpha=0.9)
    
    plt.tight_layout()
    plt.savefig(OUT_DIR / "daily_post_counts_trend.png", dpi=300)
    plt.close()

def plot_creator_composition():
    df_sum = pd.read_csv(OUT_DIR / "summary_metrics.csv")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6.5), sharey=True)
    
    years = [f"{y}年" for y in df_sum['year']]
    indices = np.arange(len(years))
    bar_width = 0.55
    
    # Left: 車載視点
    first_ob = df_sum['first_time_pct']
    ret_ob = df_sum['returning_pct']
    reg_ob = df_sum['regular_pct']
    
    ax1.bar(indices, first_ob, bar_width, label='初投稿者 (車載初投稿)', color='#2ca02c')
    ax1.bar(indices, ret_ob, bar_width, bottom=first_ob, label='復帰者 (車載>1年ブランク)', color='#ff7f0e')
    ax1.bar(indices, reg_ob, bar_width, bottom=first_ob + ret_ob, label='常連・継続投稿者 (車載視点)', color='#1f77b4')
    
    for i in range(len(years)):
        if first_ob.iloc[i] > 3:
            ax1.text(i, first_ob.iloc[i]/2, f"{df_sum['first_time_count'].iloc[i]}人\n({first_ob.iloc[i]:.1f}%)", ha='center', va='center', color='white', fontweight='bold', fontsize=10)
        if ret_ob.iloc[i] > 2:
            ax1.text(i, first_ob.iloc[i] + ret_ob.iloc[i]/2, f"{df_sum['returning_count'].iloc[i]}人\n({ret_ob.iloc[i]:.1f}%)", ha='center', va='center', color='white', fontweight='bold', fontsize=10)
        ax1.text(i, first_ob.iloc[i] + ret_ob.iloc[i] + reg_ob.iloc[i]/2, f"{df_sum['regular_count'].iloc[i]}人\n({reg_ob.iloc[i]:.1f}%)", ha='center', va='center', color='white', fontweight='bold', fontsize=10)

    ax1.set_ylabel("構成比 (%)", labelpad=10)
    ax1.set_title("【車載視点】クリエイター属性内訳", pad=15)
    ax1.set_xticks(indices)
    ax1.set_xticklabels([f"{df_sum['year'].iloc[i]}年\n(N={df_sum['period_creators'].iloc[i]})" for i in range(len(df_sum))])
    ax1.set_ylim(0, 105)
    ax1.grid(True, axis='y', linestyle='--', alpha=0.5)
    ax1.legend(loc='lower center', bbox_to_anchor=(0.5, -0.25), frameon=True, ncol=1, facecolor='white', framealpha=0.9)

    # Right: ボイロ活動視点
    first_st = df_sum['first_time_st_pct']
    ret_st = df_sum['returning_st_pct']
    reg_st = df_sum['regular_st_pct']
    
    ax2.bar(indices, first_st, bar_width, label='初投稿者 (ボイロ活動初投稿)', color='#2ca02c', alpha=0.85)
    ax2.bar(indices, ret_st, bar_width, bottom=first_st, label='復帰者 (ボイロ活動>1年ブランク)', color='#ff7f0e', alpha=0.85)
    ax2.bar(indices, reg_st, bar_width, bottom=first_st + ret_st, label='常連・継続投稿者 (ボイロ活動視点)', color='#1f77b4', alpha=0.85)
    
    for i in range(len(years)):
        if first_st.iloc[i] > 3:
            ax2.text(i, first_st.iloc[i]/2, f"{df_sum['first_time_st_count'].iloc[i]}人\n({first_st.iloc[i]:.1f}%)", ha='center', va='center', color='white', fontweight='bold', fontsize=10)
        if ret_st.iloc[i] > 2:
            ax2.text(i, first_st.iloc[i] + ret_st.iloc[i]/2, f"{df_sum['returning_st_count'].iloc[i]}人\n({ret_st.iloc[i]:.1f}%)", ha='center', va='center', color='white', fontweight='bold', fontsize=10)
        ax2.text(i, first_st.iloc[i] + ret_st.iloc[i] + reg_st.iloc[i]/2, f"{df_sum['regular_st_count'].iloc[i]}人\n({reg_st.iloc[i]:.1f}%)", ha='center', va='center', color='white', fontweight='bold', fontsize=10)

    ax2.set_title("【ボイロ活動視点】クリエイター属性内訳", pad=15)
    ax2.set_xticks(indices)
    ax2.set_xticklabels([f"{df_sum['year'].iloc[i]}年\n(N={df_sum['period_creators'].iloc[i]})" for i in range(len(df_sum))])
    ax2.grid(True, axis='y', linestyle='--', alpha=0.5)
    ax2.legend(loc='lower center', bbox_to_anchor=(0.5, -0.25), frameon=True, ncol=1, facecolor='white', framealpha=0.9)

    plt.suptitle("シンプル車載動画投稿祭 参加クリエイターの属性内訳 [車載 vs ボイロ活動 2軸比較]", fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(OUT_DIR / "creator_composition_stacked.png", dpi=300)
    plt.close()

def plot_creator_composition_absolute_onboard():
    df_sum = pd.read_csv(OUT_DIR / "summary_metrics.csv")
    fig, ax = plt.subplots(figsize=(11, 6))
    
    years = [f"{y}年" for y in df_sum['year']]
    
    ax.plot(years, df_sum['period_creators'], marker='s', linewidth=3, markersize=8, label='総参加者数', color='#333333', linestyle='--')
    ax.plot(years, df_sum['regular_count'], marker='o', linewidth=2.5, markersize=8, label='常連・継続投稿者数', color='#1f77b4')
    ax.plot(years, df_sum['first_time_count'], marker='o', linewidth=2.5, markersize=8, label='初投稿者数 (車載初投稿)', color='#2ca02c')
    ax.plot(years, df_sum['returning_count'], marker='o', linewidth=2.5, markersize=8, label='復帰者数 (車載>1年ブランク)', color='#ff7f0e')
    
    for i in range(len(years)):
        ax.text(i, df_sum['period_creators'].iloc[i] + 7, f"{df_sum['period_creators'].iloc[i]}人", ha='center', va='bottom', color='#333333', fontweight='bold')
        ax.text(i, df_sum['regular_count'].iloc[i] + 7, f"{df_sum['regular_count'].iloc[i]}人", ha='center', va='bottom', color='#1f77b4', fontweight='bold')
        ax.text(i, df_sum['first_time_count'].iloc[i] + 5, f"{df_sum['first_time_count'].iloc[i]}人", ha='center', va='bottom', color='#2ca02c', fontweight='bold')
        ax.text(i, df_sum['returning_count'].iloc[i] - 3.5, f"{df_sum['returning_count'].iloc[i]}人", ha='center', va='top', color='#e65100', fontweight='bold')

    ax.set_ylabel("人数 (人)", labelpad=10)
    ax.set_title("シンプル車載動画投稿祭 属性別参加者数の推移【車載視点】(2023-2026)", pad=15)
    ax.set_ylim(-5, max(df_sum['period_creators']) + 45)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(frameon=True, facecolor='white', framealpha=0.9, loc='center right')
    
    plt.tight_layout()
    plt.savefig(OUT_DIR / "creator_composition_absolute_onboard.png", dpi=300)
    plt.close()

def plot_creator_composition_absolute_voiceroid():
    df_sum = pd.read_csv(OUT_DIR / "summary_metrics.csv")
    fig, ax = plt.subplots(figsize=(11, 6))
    
    years = [f"{y}年" for y in df_sum['year']]
    
    ax.plot(years, df_sum['period_creators'], marker='s', linewidth=3, markersize=8, label='総参加者数', color='#333333', linestyle='--')
    ax.plot(years, df_sum['regular_st_count'], marker='o', linewidth=2.5, markersize=8, label='常連・継続投稿者数 (ボイロ視点)', color='#1f77b4')
    ax.plot(years, df_sum['first_time_st_count'], marker='o', linewidth=2.5, markersize=8, label='初投稿者数 (ボイロ活動初投稿)', color='#2ca02c')
    ax.plot(years, df_sum['returning_st_count'], marker='o', linewidth=2.5, markersize=8, label='復帰者数 (ボイロ活動>1年ブランク)', color='#ff7f0e')
    
    for i in range(len(years)):
        ax.text(i, df_sum['period_creators'].iloc[i] + 7, f"{df_sum['period_creators'].iloc[i]}人", ha='center', va='bottom', color='#333333', fontweight='bold')
        ax.text(i, df_sum['regular_st_count'].iloc[i] + 7, f"{df_sum['regular_st_count'].iloc[i]}人", ha='center', va='bottom', color='#1f77b4', fontweight='bold')
        ax.text(i, df_sum['first_time_st_count'].iloc[i] + 5, f"{df_sum['first_time_st_count'].iloc[i]}人", ha='center', va='bottom', color='#2ca02c', fontweight='bold')
        ax.text(i, df_sum['returning_st_count'].iloc[i] - 3.5, f"{df_sum['returning_st_count'].iloc[i]}人", ha='center', va='top', color='#e65100', fontweight='bold')

    ax.set_ylabel("人数 (人)", labelpad=10)
    ax.set_title("シンプル車載動画投稿祭 属性別参加者数の推移【ボイロ活動視点】(2023-2026)", pad=15)
    ax.set_ylim(-5, max(df_sum['period_creators']) + 45)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(frameon=True, facecolor='white', framealpha=0.9, loc='center right')
    
    plt.tight_layout()
    plt.savefig(OUT_DIR / "creator_composition_absolute_voiceroid.png", dpi=300)
    plt.close()

def plot_days_gap_histograms():
    all_gaps_file = OUT_DIR / "all_user_gaps.csv"
    if not all_gaps_file.exists():
        return
        
    df_all = pd.read_csv(all_gaps_file)
    df_log = df_all[df_all['days_gap'] >= 0.1].copy()
    
    ticks = [0.1, 1, 7, 30, 90, 180, 365, 730, 1460, 2700]
    tick_labels = ['0.1日', '1日', '1週間', '1ヶ月', '3ヶ月', '半年', '1年', '2年', '4年', '7.5年']

    # Stacked Log scale
    fig, ax = plt.subplots(figsize=(11, 6))
    sns.histplot(data=df_log, x='days_gap', hue='year', palette='tab10', log_scale=True, bins=30, multiple='stack', ax=ax)
    ax.axvline(365, color='red', linestyle='--', linewidth=2, label='1年 (365日)')
    ax.set_xticks(ticks)
    ax.set_xticklabels(tick_labels)
    ax.set_xlabel("前回の車載動画投稿からの経過日数 [対数 (Log) 軸]", labelpad=10)
    ax.set_ylabel("投稿者数 (人)", labelpad=10)
    ax.set_title("前回車載動画投稿からの経過日数分布 [積み上げヒストグラム]", pad=15)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(frameon=True)
    plt.tight_layout()
    plt.savefig(OUT_DIR / "days_gap_histogram_log_stacked.png", dpi=300)
    plt.close()

    # Subplots by Year (4 panels vertical)
    fig, axes = plt.subplots(4, 1, figsize=(11, 12), sharex=True, sharey=True)
    colors = {2023: '#1f77b4', 2024: '#ff7f0e', 2025: '#2ca02c', 2026: '#d62728'}
    
    for i, year in enumerate([2023, 2024, 2025, 2026]):
        ax = axes[i]
        sub = df_log[df_log['year'] == year]
        sns.histplot(data=sub, x='days_gap', color=colors[year], log_scale=True, bins=30, ax=ax)
        ax.axvline(365, color='red', linestyle='--', linewidth=1.8, label='1年 (365日)' if i==0 else None)
        ax.set_ylabel("投稿者数 (人)", labelpad=8)
        ax.set_title(f"{year}年 (N={len(sub)}人)", fontsize=13, loc='left', pad=4)
        ax.grid(True, linestyle='--', alpha=0.6)
        if i == 0:
            ax.legend(frameon=True, loc='upper right')
            
    axes[3].set_xticks(ticks)
    axes[3].set_xticklabels(tick_labels)
    axes[3].set_xlabel("前回の車載動画投稿からの経過日数 [対数 (Log) 軸]", labelpad=10)
    fig.suptitle("年別の経過日数分布 [4段サブプロット - 各年比較に最適]", fontsize=16, fontweight='bold', y=0.99)
    plt.tight_layout()
    plt.savefig(OUT_DIR / "days_gap_histogram_log_subplots.png", dpi=300)
    plt.close()

    # Combined Log scale
    total_count = len(df_log)
    fig, ax = plt.subplots(figsize=(11, 6))
    sns.histplot(data=df_log, x='days_gap', color='#4c72b0', log_scale=True, bins=30, ax=ax)
    ax.axvline(365, color='red', linestyle='--', linewidth=2, label='1年 (365日)')
    ax.set_xticks(ticks)
    ax.set_xticklabels(tick_labels)
    ax.set_xlabel("前回の車載動画投稿からの経過日数 [対数 (Log) 軸]", labelpad=10)
    ax.set_ylabel("投稿者数 (人)", labelpad=10)
    ax.set_title(f"全期間合算の経過日数分布 (2023-2026 全{total_count}名) [単一分布 - 全体傾向把握に最適]", pad=15)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(frameon=True)
    plt.tight_layout()
    plt.savefig(OUT_DIR / "days_gap_histogram_log_combined.png", dpi=300)
    plt.close()

def plot_disappearance_rates():
    df_sum = pd.read_csv(OUT_DIR / "summary_metrics.csv")
    sub = df_sum[df_sum['year'] > 2023].copy()
    
    fig, ax = plt.subplots(figsize=(9, 5))
    
    years = [f"{y-1}年参加者" for y in sub['year']]
    ob_pct = sub['disappeared_ob_pct']
    st_pct = sub['disappeared_st_pct']
    
    x = np.arange(len(years))
    width = 0.35
    
    ax.bar(x - width/2, ob_pct, width, label='車載動画を二度と投稿していない割合', color='#d62728')
    ax.bar(x + width/2, st_pct, width, label='全ソフトウェアトーク動画を投稿していない割合', color='#9467bd')
    
    for i in range(len(years)):
        ax.text(i - width/2, ob_pct.iloc[i] + 0.5, f"{ob_pct.iloc[i]:.1f}%\n({sub['disappeared_ob_count'].iloc[i]}/{sub['prev_year_creators'].iloc[i]}人)", ha='center', va='bottom', fontweight='bold')
        ax.text(i + width/2, st_pct.iloc[i] + 0.5, f"{st_pct.iloc[i]:.1f}%\n({sub['disappeared_st_count'].iloc[i]}/{sub['prev_year_creators'].iloc[i]}人)", ha='center', va='bottom', fontweight='bold')

    ax.set_ylabel("失踪率 (%)", labelpad=10)
    ax.set_title("シンプル車載投稿祭 参加者の翌年失踪率 (2023-2025参加者)", pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(years)
    ax.set_ylim(0, max(ob_pct.max(), st_pct.max()) + 5)
    ax.grid(True, axis='y', linestyle='--', alpha=0.5)
    ax.legend(frameon=True)
    
    plt.tight_layout()
    plt.savefig(OUT_DIR / "disappearance_rates.png", dpi=300)
    plt.close()

if __name__ == '__main__':
    plot_daily_counts()
    plot_creator_composition()
    plot_creator_composition_absolute_onboard()
    plot_creator_composition_absolute_voiceroid()
    plot_days_gap_histograms()
    plot_disappearance_rates()
