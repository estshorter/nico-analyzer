# /// script
# dependencies = [
#   "matplotlib",
#   "matplotlib-fontja",
#   "pandas",
#   "seaborn",
#   "numpy",
# ]
# ///

import pickle
import matplotlib.pyplot as plt
import matplotlib_fontja
import pandas as pd
import seaborn as sns
import numpy as np
from pathlib import Path
from matplotlib.ticker import FuncFormatter
from common_utils import filter_software_talk

# グラフのスタイル設定
plt.rcParams['font.family'] = ['IBM Plex Sans JP', 'BIZ UDGothic', 'Yu Gothic', 'Meiryo', 'MS Gothic', 'sans-serif']
plt.rcParams['font.weight'] = 'bold'
plt.rcParams['font.size'] = 16
plt.rcParams['axes.titlesize'] = 24
plt.rcParams['axes.labelsize'] = 20
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['legend.fontsize'] = 16
plt.rcParams['xtick.labelsize'] = 16
plt.rcParams['ytick.labelsize'] = 16
plt.rcParams['figure.dpi'] = 200

# ハイライト対象のユーザーID
HIGHLIGHT_USER_IDS = [980198, 130380191, 1594318, 134979178, 97437895]

# ジャンルの日本語名マッピング
GENRE_MAP = {
    "game": "ゲーム",
    "theater": "劇場",
    "explanation": "解説",
    "kitchen": "キッチン",
    "onboard": "車載",
    "travel": "旅行",
    "software_talk": "ボイロ全体"
}

def load_data(file_name, is_software_talk=False):
    input_path = Path(f"results/{file_name}.pickle")
    if not input_path.exists():
        print(f"File not found: {input_path}")
        return None

    with open(input_path, "rb") as f:
        raw_data = pickle.load(f)
    
    if isinstance(raw_data, dict) and "data" in raw_data:
        data = raw_data["data"]
    else:
        data = raw_data

    if isinstance(data, list):
        df = pd.DataFrame(data)
    elif isinstance(data, pd.DataFrame):
        df = data
    else:
        print(f"Unexpected data format for {file_name}: {type(data)}")
        return None
        
    if "viewCounter" not in df.columns or "likeCounter" not in df.columns or "startTime" not in df.columns or "userId" not in df.columns or "lengthSeconds" not in df.columns:
        print(f"Missing columns in {file_name}. Available columns: {df.columns.tolist()}")
        return None

    # ソフトウェアトーク全体の場合は、既存のフィルター（歌関係の除外）を適用
    if is_software_talk:
        df = filter_software_talk(df)

    df["startTime"] = pd.to_datetime(df["startTime"])
    df = df[df["startTime"].dt.year == 2025].copy()
    
    if df.empty:
        print(f"No data for 2025 in {file_name}")
        return None

    # 再生数300回以上の動画に限定（低再生数による外れ値ノイズを除外）
    df = df[df["viewCounter"] >= 300].copy()
    
    if df.empty:
        print(f"No data after 300 views filter in {file_name}")
        return None

    df["likeRatio"] = df["likeCounter"] / df["viewCounter"]
    df["genre"] = GENRE_MAP.get(file_name, file_name)
    
    # ハイライトフラグの追加
    df["is_highlight"] = df["userId"].isin(HIGHLIGHT_USER_IDS)
    
    return df

def plot_length_ratio(file_name, highlight=True, is_software_talk=False):
    df = load_data(file_name, is_software_talk=is_software_talk)
    if df is None:
        return

    dir_name = "length_vs_like" if highlight else "length_vs_like_standard"
    output_dir = Path(f"results/{dir_name}")
    output_dir.mkdir(parents=True, exist_ok=True)
    suffix = "" if highlight else "_standard"
    output_path = output_dir / f"length_vs_like_{file_name}{suffix}.png"
    
    plt.figure(figsize=(12, 8))
    
    genre_jp = GENRE_MAP.get(file_name, file_name)
    
    if highlight:
        # 通常の動画
        sns.scatterplot(data=df[~df["is_highlight"]], x="lengthSeconds", y="likeRatio", 
                        color="gray", alpha=0.3, s=30, label="Other Users")
        # ハイライト対象
        highlight_df = df[df["is_highlight"]]
        if not highlight_df.empty:
            sns.scatterplot(data=highlight_df, x="lengthSeconds", y="likeRatio", 
                            color="#E63946", alpha=0.8, s=70, edgecolor="black", linewidth=0.8, label="Target Users")
    else:
        # ハイライトなし
        color = "darkorange" if is_software_talk else "steelblue"
        sns.scatterplot(data=df, x="lengthSeconds", y="likeRatio", 
                        color=color, alpha=0.5, s=30)
    
    # 区間ごとの中央値の推移を追加 (1, 2, 5 シリーズを時間に適用)
    # 30秒, 1分(60), 2分(120), 5分(300), 10分(600), 20分(1200), 50分(3000), 100分(6000)
    bins = [0, 30, 60, 120, 300, 600, 1200, 3000, 6000]
    df['length_bin'] = pd.cut(df['lengthSeconds'], bins=bins)
    grouped = df.groupby('length_bin', observed=False)
    median_like_ratio = grouped['likeRatio'].median()
    count_df = grouped['lengthSeconds'].count()
    
    valid_bins = count_df[count_df >= 10].index
    if not valid_bins.empty:
        plot_x = []
        plot_y = []
        for b in valid_bins:
            geom_mean = np.sqrt(b.left * b.right) if b.left > 0 else b.right / 2
            plot_x.append(geom_mean)
            plot_y.append(median_like_ratio[b])
        plt.plot(plot_x, plot_y, color='black', marker='o', linestyle='-', linewidth=2.5, markersize=8, label='区間中央値の推移', zorder=10)

    plt.xscale("log")
    plt.xlim(10, 6000) # 10秒〜100分
    plt.ylim(0, 0.5)
    
    plt.xlabel("動画時間 (秒)")
    plt.ylabel("いいね率 (%)")
    plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x*100:g}'))
    
    # 秒数を分に変換した補助目盛りを表示（任意）
    plt.xticks([30, 60, 300, 600, 1200, 3600], ["30s", "1m", "5m", "10m", "20m", "1h"])
    
    plt.title(f"動画時間 vs いいね率 (2025年) - {genre_jp}")
    plt.grid(True, which="both", ls="-", alpha=0.2)
    if highlight:
        plt.legend()
    
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Generated plot: {output_path}")

def main():
    genres = ["onboard", "travel", "kitchen", "explanation", "theater", "game"]
    for highlight in [True, False]:
        for genre in genres:
            plot_length_ratio(genre, highlight=highlight)
        plot_length_ratio("software_talk", highlight=highlight, is_software_talk=True)

if __name__ == "__main__":
    main()
