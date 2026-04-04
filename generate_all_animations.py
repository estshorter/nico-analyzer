# -*- coding: utf-8 -*-
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
import sys

# FFmpeg configuration
plt.rcParams['animation.ffmpeg_path'] = r"C:\Users\estshorter\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin\ffmpeg.exe"

def get_icon_color(icon_path):
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
    except:
        pass
    return None

def find_icon(char_name, icon_dir):
    """改良版アイコン検索ロジック"""
    # 1. ルートディレクトリの全ファイルを小文字・クリーン化したマップを作成
    available_icons = {f.stem.lower().replace(" ","").replace("　",""): f for f in icon_dir.glob("*.png")}
    
    # ニックネーム・別名マッピング (正規化済み)
    nicknames = {
        "結月ゆかり": ["ゆかりさん", "ゆかり"],
        "琴葉茜": ["あかねちゃん", "あかね"],
        "琴葉葵": ["あおいちゃん", "あおい"],
        "紲星あかり": ["あかりん", "あかり"],
        "東北きりたん": ["きりたん"],
        "東北ずん子": ["ずんちゃん", "ずん子"],
        "東北イタコ": ["イタコ姉さま", "イタコ"],
        "ずんだもん": ["ずんだもん"],
        "四国めたん": ["めたんちゃん", "めたん"],
        "春日部つむぎ": ["つむぎちゃん", "つむぎ"],
        "弦巻マキ": ["マキマキ", "マキ"],
        "音街ウナ": ["ウナちゃん", "ウナ"],
        "宮舞モカ": ["モカちゃん", "モカ"],
        "さとうささら": ["ささらん", "ささら"],
        "すずきつづみ": ["つづみん", "つづみ"],
        "京町セイカ": ["セイカさん", "セイカ"],
        "タカハシ": ["タカハシ（真）"],
    }

    char_clean = char_name.lower().replace(" ", "").replace("　", "")
    
    # a. ルートディレクトリから直接一致
    if char_clean in available_icons:
        return available_icons[char_clean]
        
    # b. ニックネームでルートディレクトリを検索
    if char_name in nicknames:
        for nick in nicknames[char_name]:
            nick_clean = nick.lower().replace(" ","").replace("　","")
            if nick_clean in available_icons:
                return available_icons[nick_clean]
                
    # c. サブディレクトリを検索
    for sub in icon_dir.iterdir():
        if sub.is_dir():
            sub_name_clean = sub.name.lower().replace(" ","").replace("　","")
            # サブディレクトリ名がキャラ名やニックネームと一致するか
            match_sub = False
            if sub_name_clean == char_clean:
                match_sub = True
            elif char_name in nicknames:
                for nick in nicknames[char_name]:
                    if sub_name_clean == nick.lower().replace(" ","").replace("　",""):
                        match_sub = True
                        break
            
            if match_sub or char_clean in sub_name_clean:
                pngs = list(sub.glob("*.png"))
                if pngs:
                    return pngs[0]

    # d. あいまい一致
    for icon_name_clean, icon_path in available_icons.items():
        if icon_name_clean in char_clean or char_clean in icon_name_clean:
            return icon_path
            
    return None

def create_animation(category, cat_label):
    input_path = Path(f"results/history/cache/{category}_processed.csv")
    icon_dir = Path("icons")
    output_dir = Path(f"results/history")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{category}_ranking_history_count.mp4"
    debug_dir = output_dir / "debug_frames"
    debug_dir.mkdir(parents=True, exist_ok=True)
    
    if not input_path.exists():
        print(f"Error: Cache data not found at {input_path}.")
        return

    print(f"Loading data for {category}...")
    df = pd.read_csv(input_path, encoding="utf-8-sig")
    df = df[(df["year"] >= 2011) & (df["year"] <= 2025)]
    
    yearly_counts = df.groupby(["year", "character"])["contentId"].nunique().reset_index()
    yearly_counts.columns = ["year", "character", "postCount"]
    df_wide = yearly_counts.pivot(index="year", columns="character", values="postCount")
    
    df_rank = df_wide.rank(axis=1, ascending=False, method='min')
    df_rank[df_rank > 10] = 11
    
    target_chars = df_rank.loc[2025][df_rank.loc[2025] <= 10].index.tolist()
    ever_top10 = df_rank[df_rank <= 10].dropna(how='all', axis=1).columns.tolist()
    other_chars = [c for c in ever_top10 if c not in target_chars]
    
    char_icons = {}
    char_colors = {}
    palette = plt.cm.tab20(np.linspace(0, 1, 40))
    
    print(f"--- Icon Matching for {category} ---")
    all_target_chars = target_chars + other_chars
    for i, char in enumerate(all_target_chars):
        matched_icon = find_icon(char, icon_dir)
        if matched_icon:
            char_icons[char] = matched_icon
            extracted_color = get_icon_color(matched_icon)
            char_colors[char] = extracted_color if extracted_color is not None else palette[i % len(palette)]
            if char in target_chars:
                print(f"  [TOP10] {char} -> {matched_icon}")
        else:
            char_colors[char] = palette[i % len(palette)]
            if char in target_chars:
                print(f"  [MISS ] {char} (No icon found)")

    years = sorted(df_rank.index.tolist())
    steps_per_year = 40
    frames_main = (len(years) - 1) * steps_per_year + 1
    hold_frames = 120 
    total_frames = frames_main + hold_frames
    
    fig, ax = plt.subplots(figsize=(16, 9))
    fig.subplots_adjust(left=0.08, right=0.92, top=0.9, bottom=0.1)
    
    try:
        matplotlib_fontja.japanize()
    except:
        plt.rcParams['font.family'] = ['Meiryo', 'Yu Gothic', 'MS Gothic']

    pe = [path_effects.withStroke(linewidth=2, foreground="white")]
    icon_images_cache = {}

    def get_image(path):
        path_str = str(path)
        if path_str not in icon_images_cache:
            img = plt.imread(path_str)
            if len(img.shape) == 3 and img.shape[2] == 3:
                new_img = np.ones((img.shape[0], img.shape[1], 4))
                new_img[:, :, :3] = img
                img = new_img
            icon_images_cache[path_str] = OffsetImage(img, zoom=0.06)
        return icon_images_cache[path_str]

    def update(frame):
        ax.clear()
        ax.set_xlim(2010.5, 2025.5)
        ax.set_ylim(10.5, 0.5)
        ax.set_yticks(range(1, 11))
        ax.set_xticks(years)
        ax.set_xticklabels([str(y) for y in years])
        
        effective_frame = min(frame, frames_main - 1)
        year_idx = effective_frame // steps_per_year
        alpha = (effective_frame % steps_per_year) / steps_per_year
        current_year_val = years[year_idx] + alpha
        
        ax.set_title(f"{cat_label} キャラクター人気順位推移 (投稿数) ({int(years[year_idx])}年)", fontsize=28, pad=20)
        ax.set_xlabel("年", fontsize=18)
        ax.set_ylabel("順位 (1-10位)", fontsize=18)
        ax.grid(True, axis='both', linestyle='--', alpha=0.3)
        
        # Draw background
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
            
            ax.plot(display_x, display_y, color="#888888", linewidth=2.0, alpha=0.3, zorder=1)
            current_val_bg = display_y[-1]
            if not np.isnan(current_val_bg) and current_val_bg <= 10.4:
                if char in char_icons:
                    ab = AnnotationBbox(get_image(char_icons[char]), (display_x[-1], display_y[-1]), 
                                        frameon=False, xybox=(0, 0), xycoords='data', 
                                        boxcoords="offset points", box_alignment=(0.5, 0.5), zorder=3)
                    ax.add_artist(ab)
                else:
                    ax.text(display_x[-1] + 0.2, display_y[-1], char, color="#888888", 
                            fontsize=12, weight='bold', va='center', path_effects=pe, zorder=3, clip_on=False)

        # Draw main
        for char in target_chars:
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
                    current_val = p1 * (1 - alpha) + p2 * alpha
                    display_x.append(current_year_val)
                    display_y.append(current_val)
            
            ax.plot(display_x, display_y, color=char_colors[char], linewidth=5, alpha=0.8, zorder=2)
            current_val = display_y[-1]
            if not np.isnan(current_val) and current_val <= 10.4:
                if char in char_icons:
                    ab = AnnotationBbox(get_image(char_icons[char]), (display_x[-1], display_y[-1]), 
                                        frameon=False, xybox=(0, 0), xycoords='data', 
                                        boxcoords="offset points", box_alignment=(0.5, 0.5), zorder=4)
                    ax.add_artist(ab)
                else:
                    ax.text(display_x[-1] + 0.2, display_y[-1], char, color=char_colors[char], 
                            fontsize=16, weight='bold', va='center', path_effects=pe, zorder=4, clip_on=False)

    # Debug: Save frames to check if icons appear in static output
    update(0)
    fig.savefig(debug_dir / f"{category}_first_frame.png")
    update(total_frames - 1)
    fig.savefig(debug_dir / f"{category}_last_frame.png")

    print(f"Generating animation for {category} ({total_frames} frames)...")
    ani = animation.FuncAnimation(fig, update, frames=total_frames, interval=40)
    ani.save(str(output_file), writer='ffmpeg', fps=24, dpi=100)
    plt.close()
    print(f"Saved {output_file}")

def main():
    # Requested order: 全体, 実況, 劇場, 解説, キッチン, 車載, 旅行
    categories = ["software_talk", "game", "theater", "explanation", "kitchen", "onboard", "travel"]
    cat_labels = {
        "software_talk": "ソフトウェアトーク全体",
        "game": "実況",
        "theater": "劇場",
        "explanation": "解説",
        "kitchen": "キッチン",
        "onboard": "車載",
        "travel": "旅行"
    }
    for cat in categories:
        create_animation(cat, cat_labels[cat])

if __name__ == "__main__":
    main()
