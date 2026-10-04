# /// script
# dependencies = [
#   "matplotlib",
#   "matplotlib-fontja",
#   "pandas",
#   "numpy",
# ]
# ///

import pickle
from pathlib import Path
import matplotlib_fontja
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from common_utils import filter_software_talk

def preprocess(category):
    pickle_path = Path(f"results/{category}.pickle")
    if not pickle_path.exists():
        return None
    with open(pickle_path, "rb") as f:
        recv = pickle.load(f)
    df = pd.json_normalize(recv["data"])
    if category == "software_talk":
        df = filter_software_talk(df)
    df["startTime"] = pd.to_datetime(df["startTime"])
    df["year"] = df["startTime"].dt.year
    df["viewCounter"] = df["viewCounter"].astype(float)
    return df

def get_stats(category):
    df = preprocess(category)
    if df is None: return None
    data_2025 = df[df["year"] == 2025]["viewCounter"].values
    if len(data_2025) == 0: return None
    
    # 中央値 (50%) と 上位30% (70%タイル)
    median = np.median(data_2025)
    top30_threshold = np.percentile(data_2025, 70)
    return int(median), int(top30_threshold)

def create_dark_report_table(data, filename, col_labels):
    matplotlib_fontja.japanize()
    
    # 配色設定 (ダークモード)
    bg_color = '#1e1e1e'      # 背景：ダークグレー
    header_color = '#333333'  # ヘッダー：濃いグレー
    cell_bg_color = '#252526' # セル背景：少し明るいグレー
    text_color = '#d4d4d4'    # テキスト：薄いグレー
    border_color = '#444444'  # 境界線：グレー
    accent_color = '#3794ff'  # アクセント（数値など）：青
    
    # 図のサイズ調整
    fig, ax = plt.subplots(figsize=(10, len(data) * 0.8 + 1))
    fig.patch.set_facecolor(bg_color)
    ax.axis('off')
    
    # テーブル作成
    table = ax.table(cellText=data, colLabels=col_labels, loc='center', cellLoc='center')
    
    # スタイルの設定
    table.auto_set_font_size(False)
    table.set_fontsize(20)
    table.scale(1.2, 3.0) 
    
    for (row, col), cell in table.get_celld().items():
        # ヘッダーの設定
        if row == 0:
            cell.set_text_props(weight='bold', color='#ffffff')
            cell.set_facecolor(header_color)
        # ボディの設定
        else:
            cell.set_facecolor(cell_bg_color)
            cell.set_text_props(color=text_color)
            if col == 0: # ジャンル名/段階名
                cell.set_text_props(weight='bold', color='#ffffff')
            else: # 数値データなど
                cell.set_text_props(color=accent_color)
        
        # 罫線の色
        cell.set_edgecolor(border_color)
        cell.set_linewidth(1.5)

    plt.savefig(f"results/{filename}", dpi=300, bbox_inches='tight', facecolor=bg_color, transparent=False)
    plt.close()
    print(f"Saved (Dark Mode): results/{filename}")

def main():
    # 1. 車載動画の目標表
    onboard_stats = get_stats("onboard")
    if onboard_stats:
        onboard_data = [
            ["第一目標 (中央値)", f"{onboard_stats[0]:,} 再生", "界隈の中核・固定ファン層"],
            ["第二目標 (上位30%)", f"{onboard_stats[1]:,} 再生", "差別化が必要なトップ層"]
        ]
        create_dark_report_table(onboard_data, "table_onboard_targets_dark.png", 
                           ["目標段階", "再生数目安", "統計的意義 / 戦略"])

    # 2. 全ジャンルの比較表
    genre_order = [
        ("onboard", "車載"),
        ("game", "実況"),
        ("theater", "劇場"),
        ("explanation", "解説"),
        ("kitchen", "キッチン"),
        ("travel", "旅行")
    ]
    
    all_genre_data = []
    for cat, name in genre_order:
        stats = get_stats(cat)
        if stats:
            all_genre_data.append([name, f"{stats[0]:,}", f"{stats[1]:,}"])
            
    if all_genre_data:
        create_dark_report_table(all_genre_data, "table_all_genres_targets_dark.png", 
                           ["ジャンル", "第一目標 (中央値)", "第二目標 (上位30%)"])

if __name__ == "__main__":
    main()
