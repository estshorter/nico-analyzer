import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib_fontja
from pathlib import Path

def main():
    csv_path = Path('results/comparison/nico_vs_voiro.csv')
    df = pd.read_csv(csv_path)
    
    # Filter for 2011 onwards
    df_plot = df[df['year'] >= 2011].copy()
    
    # Set style
    sns.set_theme(style="whitegrid")
    matplotlib_fontja.japanize()

    plt.figure(figsize=(12, 6))
    
    # Plot only the post count ratio
    sns.lineplot(data=df_plot, x='year', y='video_ratio_percent', marker='o', linewidth=2.5, color='tab:blue', label='投稿数シェア')
    
    # Add values on points
    for x, y in zip(df_plot['year'], df_plot['video_ratio_percent']):
        plt.text(x, y + 0.5, f'{y:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold', color='tab:blue')

    plt.title('ニコニコ全体におけるボイロ界隈の投稿数シェア推移', fontsize=16)
    plt.ylabel('シェア (%)', fontsize=12)
    plt.xlabel('年', fontsize=12)
    plt.xticks(df_plot['year'], rotation=45)
    plt.ylim(0, df_plot['video_ratio_percent'].max() * 1.2)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()

    plt.tight_layout()
    
    output_path = Path('results/comparison/nico_vs_voiro_ratio.png')
    plt.savefig(output_path, dpi=300)
    print(f"Graph saved to {output_path}")

if __name__ == "__main__":
    main()
