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
import matplotlib.animation as animation
import matplotlib.patheffects as path_effects
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib_fontja
from pathlib import Path
from PIL import Image

# FFmpeg configuration
plt.rcParams['animation.ffmpeg_path'] = r"C:\Users\estshorter\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe"

def get_icon_color(icon_path):
    """アイコン画像からメインカラーを抽出する (白と濃いグレー#555555を除く)"""
    try:
        with Image.open(icon_path) as img:
            img = img.convert("RGBA")
            data = np.array(img)
            # アルファ値が一定以上のピクセルのみ抽出
            visible_pixels = data[data[:, :, 3] > 128][:, :3]
            
            if len(visible_pixels) > 0:
                # 特定の色を除外するフィルタ
                # 白 (すべて240以上) を除外
                is_white = np.all(visible_pixels > 240, axis=1)
                # 濃いグレー #555555 付近 (80-90) を除外
                is_grey = np.all((visible_pixels > 70) & (visible_pixels < 100), axis=1)
                
                filtered_pixels = visible_pixels[~(is_white | is_grey)]
                
                if len(filtered_pixels) > 0:
                    avg_color = filtered_pixels.mean(axis=0) / 255.0
                    return avg_color
    except Exception as e:
        print(f"Warning: Could not extract color from {icon_path}: {e}")
    return None

def create_animation():
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
    # 順位変換 (NaNはそのまま)
    df_rank = df_wide.rank(axis=1, ascending=False, method='min')
    # 10位より下をカット (11位として扱う)
    df_rank[df_rank > 10] = 11
    
    # 登場キャラの抽出
    # メイン: 2025年のTOP10
    target_chars = df_rank.loc[2025][df_rank.loc[2025] <= 10].index.tolist()
    # 背景: 2025年TOP10以外で、過去に一度でも10位以内に入ったキャラ
    ever_top10 = df_rank[df_rank <= 10].dropna(how='all', axis=1).columns.tolist()
    other_chars = [c for c in ever_top10 if c not in target_chars]
    
    print(f"Target characters (Top 10 in 2025): {len(target_chars)}")
    print(f"Background characters (Historical Top 10): {len(other_chars)}")
    
    # アイコンと色の紐付け
    char_icons = {}
    char_colors = {}
    
    # 既存の全アイコンファイルをリスト化
    available_icons = {f.stem: f for f in icon_dir.glob("*.png")}
    
    # デフォルトパレット (多めに用意)
    palette = plt.cm.tab20(np.linspace(0, 1, 40))
    
    # メイン + 背景 の全キャラに対してマッチング
    all_target_chars = target_chars + other_chars
    for i, char in enumerate(all_target_chars):
        matched_icon = None
        char_clean = char.replace(" ", "").replace("　", "")
        # 1. 完全一致 (クリーン後)
        if char_clean in available_icons:
            matched_icon = available_icons[char_clean]
        else:
            # 2. あいまい一致 (ファイル名がキャラ名に含まれているか)
            for icon_name, icon_path in available_icons.items():
                icon_clean = icon_name.replace(" ", "").replace("　", "")
                if icon_clean in char_clean or char_clean in icon_clean:
                    matched_icon = icon_path
                    break
        
        if matched_icon:
            char_icons[char] = matched_icon
            extracted_color = get_icon_color(matched_icon)
            if extracted_color is not None:
                char_colors[char] = extracted_color
            else:
                char_colors[char] = palette[i % len(palette)]
            print(f"Matched icon: {char} -> {matched_icon.name}")
        else:
            char_colors[char] = palette[i % len(palette)]
            if char in target_chars or char in other_chars:
                print(f"FAILED to match icon: {char}")

    # アニメーション設定
    years = sorted(df_rank.index.tolist())
    steps_per_year = 30 * 2
    frames = (len(years) - 1) * steps_per_year + 1
    
    fig, ax = plt.subplots(figsize=(16, 9))
    # 余白を固定してガタつきを防止
    fig.subplots_adjust(left=0.08, right=0.92, top=0.9, bottom=0.1)
    
    try:
        matplotlib_fontja.japanize()
    except:
        plt.rcParams['font.family'] = ['Meiryo', 'Yu Gothic', 'MS Gothic']

    pe = [path_effects.withStroke(linewidth=2, foreground="white")]

    # アイコン読み込み用キャッシュ
    icon_images_cache = {}

    def get_image(path):
        if path not in icon_images_cache:
            img = plt.imread(path)
            icon_images_cache[path] = OffsetImage(img, zoom=0.06) # さらに縮小
        return icon_images_cache[path]

    def update(frame):
        ax.clear()
        # 軸と範囲を固定 (10位まで表示)
        ax.set_xlim(2010.5, 2025.5)
        ax.set_ylim(10.5, 0.5)
        ax.set_yticks(range(1, 11))
        ax.set_xticks(years)
        ax.set_xticklabels([str(y) for y in years])
        
        year_idx = frame // steps_per_year
        alpha = (frame % steps_per_year) / steps_per_year
        current_year_val = years[year_idx] + alpha
        
        ax.set_title(f"ボイロキャラクター人気順位推移 ({int(years[year_idx])}年)", fontsize=28, pad=20)
        ax.set_xlabel("年", fontsize=18)
        ax.set_ylabel("順位 (再生数)", fontsize=18)
        ax.grid(True, axis='both', linestyle='--', alpha=0.3)
        
        # 1. 背景の線を先に描画 (過去10位以内に入ったキャラ)
        for char in other_chars:
            y_data_all = df_rank[char].values
            valid_mask = ~np.isnan(y_data_all)
            if not np.any(valid_mask): continue
            start_idx = np.where(valid_mask)[0][0]
            if year_idx < start_idx: continue
            
            display_x = list(years[start_idx:year_idx + 1])
            display_y = list(y_data_all[start_idx:year_idx + 1])
            
            if year_idx < len(years) - 1:
                p1, p2 = y_data_all[year_idx], y_data_all[year_idx + 1]
                if not np.isnan(p2):
                    display_x.append(current_year_val)
                    display_y.append(p1 * (1 - alpha) + p2 * alpha)
            
            # 10位以内の期間があるキャラを濃いめのグレーで描画
            ax.plot(display_x, display_y, color="#888888", linewidth=2.0, alpha=0.5, zorder=1)
            
            # 背景キャラの先端にアイコンまたは名前を表示 (圏内にいる場合のみ)
            current_val_bg = display_y[-1]
            if not np.isnan(current_val_bg) and current_val_bg <= 10.4:
                if char in char_icons:
                    ab = AnnotationBbox(get_image(char_icons[char]), (display_x[-1], display_y[-1]), 
                                        frameon=False, xybox=(0, 0), xycoords='data', 
                                        boxcoords="offset points", box_alignment=(0.5, 0.5), zorder=1)
                    ax.add_artist(ab)
                else:
                    ax.text(display_x[-1] + 0.1, display_y[-1], char, color="#888888", 
                            fontsize=12, weight='bold', va='center', path_effects=pe, alpha=0.7, zorder=1)

        # 2. メインの10人を描画 (target_chars)
        for char in target_chars:
            y_data_all = df_rank[char].values
            x_data_all = np.array(years)
            
            # 初登場インデックスを確認
            valid_mask = ~np.isnan(y_data_all)
            if not np.any(valid_mask): continue
            start_idx = np.where(valid_mask)[0][0]
            
            # 現在のフレームが初登場前なら描画しない
            if year_idx < start_idx: continue
            
            # 描画用スライス
            display_x = list(x_data_all[start_idx:year_idx + 1])
            display_y = list(y_data_all[start_idx:year_idx + 1])
            
            current_val = y_data_all[year_idx]
            
            if year_idx < len(years) - 1:
                # 次の年への補間
                p1 = y_data_all[year_idx]
                p2 = y_data_all[year_idx + 1]
                
                if not np.isnan(p2):
                    # 次の年もある場合は滑らかに繋ぐ
                    current_val = p1 * (1 - alpha) + p2 * alpha
                    display_x.append(current_year_val)
                    display_y.append(current_val)
                elif alpha > 0:
                    # 次の年がない（ここで消える）場合は、補間せずそのまま止めるか消す
                    # ここではその年の終わりにパッと消える挙動にする
                    pass

            ax.plot(display_x, display_y, color=char_colors[char], linewidth=5, alpha=0.8)
            
            # アイコンまたは名前の表示
            if not np.isnan(current_val) and current_val <= 10.4:
                if char in char_icons:
                    ab = AnnotationBbox(get_image(char_icons[char]), (display_x[-1], display_y[-1]), 
                                        frameon=False, xybox=(0, 0), xycoords='data', 
                                        boxcoords="offset points", box_alignment=(0.5, 0.5))
                    ax.add_artist(ab)
                else:
                    ax.text(display_x[-1] + 0.1, display_y[-1], char, color=char_colors[char], 
                            fontsize=16, weight='bold', va='center', path_effects=pe)

    print(f"Generating animation with icons ({frames} frames)...")
    ani = animation.FuncAnimation(fig, update, frames=frames, interval=60)
    
    output_path = output_dir / "character_ranking_history_icons.mp4"
    print(f"Saving to {output_path}...")
    ani.save(output_path, writer='ffmpeg', fps=24, dpi=120)
    plt.close()
    print("Done!")

if __name__ == "__main__":
    create_animation()
