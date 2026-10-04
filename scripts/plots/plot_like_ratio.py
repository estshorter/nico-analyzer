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

# グラフのスタイル設定 (プロジェクトの他スクリプトに合わせる)
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
        
    if "viewCounter" not in df.columns or "likeCounter" not in df.columns or "startTime" not in df.columns or "userId" not in df.columns:
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

    df = df[df["viewCounter"] > 0].copy()
    df["likeRatio"] = df["likeCounter"] / df["viewCounter"]
    df["genre"] = GENRE_MAP.get(file_name, file_name)
    
    # ハイライトフラグの追加
    df["is_highlight"] = df["userId"].isin(HIGHLIGHT_USER_IDS)
    
    return df

def plot_ratio(file_name, highlight=True, is_software_talk=False):
    df = load_data(file_name, is_software_talk=is_software_talk)
    if df is None:
        return

    dir_name = "like_ratio" if highlight else "like_ratio_standard"
    output_dir = Path(f"results/{dir_name}")
    output_dir.mkdir(parents=True, exist_ok=True)
    suffix = "" if highlight else "_standard"
    output_path = output_dir / f"like_ratio_{file_name}{suffix}.png"
    
    plt.figure(figsize=(12, 8))
    
    genre_jp = GENRE_MAP.get(file_name, file_name)
    
    if highlight:
        # 通常の動画を先に描画
        sns.scatterplot(data=df[~df["is_highlight"]], x="viewCounter", y="likeRatio", 
                        color="gray", alpha=0.3, s=30, label="Other Users")
        
        # ハイライト対象の動画を後から（上に）描画
        highlight_df = df[df["is_highlight"]]
        if not highlight_df.empty:
            sns.scatterplot(data=highlight_df, x="viewCounter", y="likeRatio", 
                            color="#E63946", alpha=0.8, s=70, edgecolor="black", linewidth=0.8, label="Target Users")
    else:
        # ハイライトなし
        color = "darkorange" if is_software_talk else "steelblue"
        sns.scatterplot(data=df, x="viewCounter", y="likeRatio", 
                        color=color, alpha=0.5, s=30)
    
    # 区間ごとの中央値の推移を追加
    # 対数スケールに合わせた1-2-5シリーズの区間（50〜）
    bins = [50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000, 200000, 500000, 1000000]
    df['view_bin'] = pd.cut(df['viewCounter'], bins=bins)
    
    # 区間ごとのデータ数といいね率の中央値を算出
    grouped = df.groupby('view_bin', observed=False)
    median_like_ratio = grouped['likeRatio'].median()
    count_df = grouped['viewCounter'].count()
    
    # データ数が10件未満の区間はノイズになるため除外
    valid_bins = count_df[count_df >= 10].index
    
    if not valid_bins.empty:
        plot_x = []
        plot_y = []
        for b in valid_bins:
            # 幾何平均（対数軸上の中心）を算出
            geom_mean = np.sqrt(b.left * b.right)
            plot_x.append(geom_mean)
            plot_y.append(median_like_ratio[b])
            
        # 折れ線グラフ（黒の太線）で推移を描画
        plt.plot(plot_x, plot_y, 
                 color='black', marker='o', linestyle='-', linewidth=2.5, markersize=8, 
                 label='区間中央値の推移', zorder=10)

    plt.xscale("log")
    plt.xlim(1, 10**6)
    plt.ylim(0, 0.5)
    
    # 軸ラベルの設定（日本語のみ）
    plt.xlabel("再生数")
    plt.ylabel("いいね率 (%)")
    plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x*100:g}'))
    
    # タイトルの調整
    plt.title(f"再生数 vs いいね率 (2025年) - {genre_jp}")
    plt.grid(True, which="both", ls="-", alpha=0.2)
    if highlight:
        plt.legend()
    
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Generated plot: {output_path}")

def main():
    genres = ["onboard", "travel", "kitchen", "explanation", "theater", "game"]
    
    for highlight in [True, False]:
        print(f"\nGenerating plots (highlight={highlight})...")
        # 個別ジャンル
        for genre in genres:
            plot_ratio(genre, highlight=highlight)
        # ボイロ全体
        plot_ratio("software_talk", highlight=highlight, is_software_talk=True)

if __name__ == "__main__":
    main()
