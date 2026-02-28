"""
Processing Overview:
ニコニコ全体に対するボイロ界隈の規模と影響力を可視化するためのグラフを複数生成します。
投稿数・再生数の推移を対数スケールで比較する図と、
ボイロ界隈が全体に占めるシェア（％）の推移を示す図を作成し、マクロな視点での分析結果を提供します。
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker
import matplotlib_fontja

def plot_nico_vs_voiro():
    # Load data
    df = pd.read_csv('results/comparison/nico_vs_voiro.csv')

    # Set style
    sns.set_theme(style="whitegrid")
    matplotlib_fontja.japanize()

    # Create figure with 2 subplots (Videos, Views)
    fig, axes = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

    # --- Plot 1: Video Count Comparison (Log Scale) ---
    ax1 = axes[0]
    # Plot Nico Total (Left Axis)
    sns.lineplot(data=df, x='year', y='nico_total_videos', ax=ax1, label='ニコニコ全体 (左軸)', color='tab:blue', marker='o')
    ax1.set_ylabel('ニコニコ全体 投稿数', color='tab:blue', fontsize=12)
    ax1.tick_params(axis='y', labelcolor='tab:blue')
    ax1.set_yscale('log')
    
    # Plot Voiceroid Total (Right Axis)
    ax1_twin = ax1.twinx()
    sns.lineplot(data=df, x='year', y='voiro_videos', ax=ax1_twin, label='ボイロ界隈 (右軸)', color='tab:orange', marker='s', linestyle='--')
    ax1_twin.set_ylabel('ボイロ界隈 投稿数', color='tab:orange', fontsize=12)
    ax1_twin.tick_params(axis='y', labelcolor='tab:orange')
    ax1_twin.set_yscale('log')

    ax1.set_title('年間投稿数の推移 (対数スケール比較)', fontsize=14)
    ax1.grid(True, which="both", ls="-", alpha=0.2)

    # Combine legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax1_twin.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper center')
    ax1_twin.get_legend().remove()


    # --- Plot 2: View Count Comparison (Log Scale) ---
    ax2 = axes[1]
    # Plot Nico Total (Left Axis)
    sns.lineplot(data=df, x='year', y='nico_total_views', ax=ax2, label='ニコニコ全体 (左軸)', color='tab:green', marker='o')
    ax2.set_ylabel('ニコニコ全体 再生数', color='tab:green', fontsize=12)
    ax2.tick_params(axis='y', labelcolor='tab:green')
    ax2.set_yscale('log')

    # Plot Voiceroid Total (Right Axis)
    ax2_twin = ax2.twinx()
    sns.lineplot(data=df, x='year', y='voiro_views', ax=ax2_twin, label='ボイロ界隈 (右軸)', color='tab:red', marker='s', linestyle='--')
    ax2_twin.set_ylabel('ボイロ界隈 再生数', color='tab:red', fontsize=12)
    ax2_twin.tick_params(axis='y', labelcolor='tab:red')
    ax2_twin.set_yscale('log')

    ax2.set_title('年間再生数の推移 (対数スケール比較)', fontsize=14)
    ax2.grid(True, which="both", ls="-", alpha=0.2)
    ax2.set_xlabel('年', fontsize=12)

    # Format Y-axis to show real numbers (Japan units) if possible, but log scale makes it tricky.
    # Let's keep scientific notation or plain numbers for log scale, but maybe add commas.
    ax1.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
    ax1_twin.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
    ax2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
    ax2_twin.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',')))

    # Combine legends
    lines3, labels3 = ax2.get_legend_handles_labels()
    lines4, labels4 = ax2_twin.get_legend_handles_labels()
    ax2.legend(lines3 + lines4, labels3 + labels4, loc='upper center')
    ax2_twin.get_legend().remove()

    plt.tight_layout()
    output_path = 'results/comparison/nico_vs_voiro_trend.png'
    plt.savefig(output_path, dpi=300)
    print(f"Graph saved to {output_path}")

    # --- Plot 3: Ratio (Share) Trend ---
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x='year', y='video_ratio_percent', label='投稿数シェア (%)', marker='o')
    sns.lineplot(data=df, x='year', y='view_ratio_percent', label='再生数シェア (%)', marker='s')
    
    plt.title('ニコニコ全体に占めるボイロ界隈の割合推移', fontsize=14)
    plt.ylabel('シェア (%)', fontsize=12)
    plt.xlabel('年', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    
    output_path_ratio = 'results/comparison/nico_vs_voiro_ratio.png'
    plt.savefig(output_path_ratio, dpi=300)
    print(f"Ratio graph saved to {output_path_ratio}")

if __name__ == "__main__":
    plot_nico_vs_voiro()
