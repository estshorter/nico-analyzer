# /// script
# dependencies = [
#   "matplotlib",
#   "matplotlib-fontja",
#   "pandas",
#   "numpy",
#   "Pillow",
# ]
# ///

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import matplotlib_fontja
from pathlib import Path
from PIL import Image

def get_icon_color(icon_path):
    """アイコン画像からメインカラーを抽出する (白と濃いグレー#555555を除く)"""
    try:
        with Image.open(icon_path) as img:
            img = img.convert("RGBA")
            data = np.array(img)
            visible_pixels = data[data[:, :, 3] > 128][:, :3]
            
            if len(visible_pixels) > 0:
                is_white = np.all(visible_pixels > 240, axis=1)
                is_grey = np.all((visible_pixels > 70) & (visible_pixels < 100), axis=1)
                
                filtered_pixels = visible_pixels[~(is_white | is_grey)]
                
                if len(filtered_pixels) > 0:
                    avg_color = filtered_pixels.mean(axis=0) / 255.0
                    return avg_color
    except Exception as e:
        print(f"Warning: Could not extract color from {icon_path}: {e}")
    return None

def create_thumbnail():
    input_path = Path("results/history/cache/software_talk_processed.csv")
    icon_dir = Path("icons")
    output_dir = Path("results/history")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if not input_path.exists():
        print(f"Error: Cache data not found at {input_path}.")
        return

    print("Loading and preparing data...")
    df = pd.read_csv(input_path)
    df = df[(df["year"] >= 2011) & (df["year"] <= 2025)]
    
    yearly_views = df.groupby(["year", "character"])["viewCounter"].sum().reset_index()
    df_wide = yearly_views.pivot(index="year", columns="character", values="viewCounter")
    df_rank = df_wide.rank(axis=1, ascending=False, method='min')
    
    # 11位以下は非表示にするため NaN にする
    df_rank[df_rank > 10] = np.nan
    
    # 2025年のTOP10
    target_chars = df_rank.loc[2025].dropna().index.tolist()
    
    print(f"Target characters (Top 10 in 2025): {len(target_chars)}")
    
    # アイコンと色の紐付け
    char_colors = {}
    available_icons = {f.stem: f for f in icon_dir.glob("*.png")}
    palette = plt.cm.tab20(np.linspace(0, 1, 40))
    
    for i, char in enumerate(target_chars):
        matched_icon = None
        char_clean = char.replace(" ", "").replace("　", "")
        
        if char_clean in available_icons:
            matched_icon = available_icons[char_clean]
        else:
            for icon_name, icon_path in available_icons.items():
                icon_clean = icon_name.replace(" ", "").replace("　", "")
                if icon_clean in char_clean or char_clean in icon_clean:
                    matched_icon = icon_path
                    break
        
        if matched_icon:
            extracted_color = get_icon_color(matched_icon)
            if extracted_color is not None:
                char_colors[char] = extracted_color
            else:
                char_colors[char] = palette[i % len(palette)]
        else:
            char_colors[char] = palette[i % len(palette)]

    fig, ax = plt.subplots(figsize=(16, 9))
    # サムネイル用に余白を調整
    fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02)
    
    # 背景を黒系に変更
    fig.patch.set_facecolor('#1a1a1a')
    ax.set_facecolor('#1a1a1a')
    
    try:
        matplotlib_fontja.japanize()
    except:
        plt.rcParams['font.family'] = ['Meiryo', 'Yu Gothic', 'MS Gothic']

    years = sorted(df_rank.index.tolist())
    
    # 軸の設定
    ax.set_xlim(2010.5, 2025.5)
    ax.set_ylim(10.5, 0.5)
    
    # タイトル、xlabel、ylabel、tickラベルを非表示
    ax.set_title("")
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.tick_params(left=False, bottom=False)
    
    # グリッドや枠線を非表示
    ax.grid(False)
    for spine in ax.spines.values():
        spine.set_visible(False)

    # 2025年TOP10キャラのみ描画（10位の宮舞モカは除外）
    for char in target_chars:
        # 10位（宮舞モカ）を除外
        if char == "宮舞モカ":
            continue

        y_data = df_rank[char]
        
        # ずんだもんと春日部つむぎは2021年から表示
        if "ずんだもん" in char or "春日部つむぎ" in char:
            start_year = 2021
            y_data_display = y_data.loc[start_year:].copy()
            # 2021年がNaN（11位以下）の場合、グラフの底(11位)として描画を開始する
            if pd.isna(y_data_display.loc[start_year]):
                y_data_display.loc[start_year] = 11
            years_display = [y for y in years if y >= start_year]
        else:
            y_data_display = y_data
            years_display = years

        # 全キャラ共通の線スタイルで描画
        ax.plot(years_display, y_data_display.values, color=char_colors[char], linewidth=8, alpha=0.9, zorder=2)

    output_path = output_dir / "thumbnail.png"
    print(f"Saving thumbnail to {output_path}...")
    fig.savefig(output_path, dpi=120, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print("Done!")

if __name__ == "__main__":
    create_thumbnail()
