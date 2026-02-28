# /// script
# dependencies = [
#   "matplotlib",
#   "matplotlib-fontja",
#   "pandas",
#   "numpy",
#   "imageio[ffmpeg]",
# ]
# ///

import matplotlib
matplotlib.use('Agg')
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib_fontja
from pathlib import Path
import imageio

matplotlib_fontja.japanize()

plt.rcParams['figure.autolayout'] = True
plt.rcParams['font.size'] = 16
plt.rcParams['axes.titlesize'] = 32
plt.rcParams['axes.labelsize'] = 20

def main():
    csv_path = "results/zundamon_cumulative_stats_software_talk_2020.csv"
    df = pd.read_csv(csv_path)
    years = df['year'].astype(str).tolist()
    counts = df['cumulativeViewCounter'].tolist()

    fps = 30
    seconds_per_year = 0.8 / 0.75  # 0.75x speed (~1.067s per year)
    frames_per_year = int(fps * seconds_per_year)
    total_frames = frames_per_year * len(counts)

    fig, ax = plt.subplots(figsize=(19.2, 10.88), dpi=100)
    
    output_path = "results/zundamon_cumulative_video_fullhd_clear.mp4"
    print(f"Generating CLEAR Full HD MP4 video: {output_path}")

    with imageio.get_writer(output_path, fps=fps, quality=10, codec='libx264', pixelformat='yuv420p', bitrate='12M') as writer:
        for frame in range(total_frames + fps * 2):
            ax.clear()
            
            if frame >= total_frames:
                display_counts = counts
                current_year_idx = len(counts) - 1
            else:
                current_year_idx = frame // frames_per_year
                sub_frame = frame % frames_per_year
                progress = sub_frame / frames_per_year
                
                display_counts = []
                for i in range(len(counts)):
                    if i < current_year_idx:
                        display_counts.append(counts[i])
                    elif i == current_year_idx:
                        prev_val = counts[i-1] if i > 0 else 0
                        val = prev_val + (counts[i] - prev_val) * progress
                        display_counts.append(val)
                    else:
                        display_counts.append(0)

            bars = ax.bar(years, display_counts, color='#39FF14', edgecolor='black', linewidth=2)
            ax.set_ylim(0, max(counts) * 1.1)
            ax.set_title("ずんだもん累計再生数の推移 (2020-2025)", fontweight='bold', pad=30)
            ax.set_ylabel("累計再生数 (万回)", fontweight='bold')
            ax.grid(True, axis='y', linestyle='--', alpha=0.4)

            # Y軸の目盛りを「万」単位にする
            ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: f"{int(x/10000):,}"))

            for i, bar in enumerate(bars):
                if i <= current_year_idx:
                    height = bar.get_height()
                    if height > 0:
                        # 「万」単位でカンマ区切り表示
                        label_text = f'{int(height/10000):,}万'
                        ax.text(bar.get_x() + bar.get_width()/2., height + (max(counts)*0.01),
                                label_text,
                                ha='center', va='bottom', fontweight='bold', fontsize=18, 
                                bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=2))

            fig.canvas.draw()
            image = np.frombuffer(fig.canvas.buffer_rgba(), dtype='uint8')
            image = image.reshape(fig.canvas.get_width_height()[::-1] + (4,))
            writer.append_data(image[:, :, :3])
            
            if frame % 30 == 0:
                print(f"Encoding frame {frame}/{total_frames + fps*2}...")

    plt.close()
    print(f"Done! Clear video saved to {output_path}")

if __name__ == "__main__":
    main()
