# /// script
# dependencies = [
#   "matplotlib",
#   "matplotlib-fontja",
#   "pandas",
#   "numpy",
#   "seaborn",
#   "tabulate",
# ]
# ///

import pickle
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib_fontja
import numpy as np
import seaborn as sns

def preprocess(category):
    pickle_path = Path(f"results/{category}.pickle")
    if not pickle_path.exists():
        return None
    with open(pickle_path, "rb") as f:
        recv = pickle.load(f)
    df = pd.json_normalize(recv["data"])
    df["startTime"] = pd.to_datetime(df["startTime"])
    df["year"] = df["startTime"].dt.year
    df["lengthSeconds"] = df["lengthSeconds"].astype(float)
    return df

def get_heavy_users_all_years(df, target_years):
    user_id_col = "userId" if "userId" in df.columns else "owner.id"
    all_heavy_users = set()
    
    for year in target_years:
        df_year = df[df["year"] == year]
        mask = (df_year["lengthSeconds"] >= 0) & (df_year["lengthSeconds"] <= 120)
        df_short = df_year[mask]
        counts = df_short[user_id_col].value_counts()
        heavy = counts[counts >= 100].index.tolist()
        all_heavy_users.update(map(int, heavy))
    
    sorted_users = sorted(list(all_heavy_users))
    palette = sns.color_palette("tab10", len(sorted_users))
    
    # IDをマスクするためのマッピング作成
    import string
    labels = list(string.ascii_uppercase)
    if len(sorted_users) > len(labels):
        labels = [f"{i+1}" for i in range(len(sorted_users))]
    
    user_info_map = {}
    for i, uid in enumerate(sorted_users):
        user_info_map[uid] = {
            "color": palette[i],
            "label": f"投稿者{labels[i]}"
        }
    
    return user_info_map

def generate_graph(df, year, category_label, output_path, user_info_map):
    user_id_col = "userId" if "userId" in df.columns else "owner.id"
    df_year = df[df["year"] == year]
    
    # 0-2分 (0-120秒)
    min_len = 0
    max_len = 120
    mask_short = (df_year["lengthSeconds"] >= min_len) & (df_year["lengthSeconds"] <= max_len)
    df_short = df_year[mask_short]
    
    user_counts = df_short[user_id_col].value_counts().reset_index()
    user_counts.columns = ["userId", "videoCount"]
    total_videos = user_counts["videoCount"].sum()
    
    if total_videos == 0:
        return None

    heavy_users = user_counts[user_counts["videoCount"] >= 100].copy()
    others_sum = total_videos - heavy_users["videoCount"].sum()
    
    plt.rcParams['font.family'] = ['IBM Plex Sans JP', 'BIZ UDGothic', 'Yu Gothic', 'Meiryo', 'MS Gothic', 'sans-serif']
    plt.rcParams['font.weight'] = 'bold'
    plt.rcParams['font.size'] = 14
    plt.rcParams['axes.titlesize'] = 22
    plt.rcParams['figure.dpi'] = 200

    fig, ax = plt.subplots(figsize=(15, 5))
    
    current_left = 0
    for i, row in heavy_users.iterrows():
        uid = int(row['userId'])
        p = row['videoCount'] / total_videos * 100
        info = user_info_map.get(uid)
        
        ax.barh([0], [p], left=[current_left], color=info["color"], label=info["label"], height=0.6)
        if p > 4:
            ax.text(current_left + p/2, 0, f"{info['label']}\n{p:.1f}%\n({int(row['videoCount'])}本)", 
                    ha='center', va='center', color='white', fontweight='bold', fontsize=11)
        current_left += p
        
    p_others = others_sum / total_videos * 100
    ax.barh([0], [p_others], left=[current_left], color="#d1d5db", label="Others", height=0.6)
    if p_others > 5:
        ax.text(current_left + p_others/2, 0, f"その他\n({int(others_sum)}本)", 
                ha='center', va='center', color='black', fontweight='bold', fontsize=12)

    plt.title(f"{year}年 {category_label}ジャンル 0-2分動画の占有率 (全{int(total_videos)}本)", pad=20)
    ax.set_xlabel("シェア (%)")
    ax.set_yticks([])
    ax.set_xlim(0, 100)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    
    heavy_data = []
    for i, row in heavy_users.iterrows():
        uid = int(row['userId'])
        heavy_data.append({
            "label": user_info_map[uid]["label"],
            "videoCount": row['videoCount']
        })
    
    return {
        "year": year,
        "total": total_videos,
        "heavy": heavy_data
    }

def main():
    category = "explanation"
    label = "解説"
    df = preprocess(category)
    if df is None: return

    target_years = [2023, 2024, 2025]
    user_info_map = get_heavy_users_all_years(df, target_years)

    report_data = []
    for year in target_years:
        output_path = f"results/explanation/explanation_0to2m_stacked_bar_{year}.png"
        res = generate_graph(df, year, label, output_path, user_info_map)
        if res:
            report_data.append(res)

    # Markdownレポート作成
    md_content = "# 解説ジャンル (0-2分) 超アクティブ投稿者(100本以上) 分析レポート\n\n"
    md_content += "※ ユーザーIDはプライバシー保護のためマスクしています。\n\n"
    for item in report_data:
        md_content += f"## {item['year']}年\n"
        md_content += f"- **0-2分動画 総投稿数: {int(item['total'])}本**\n\n"
        md_content += "| 投稿者ラベル | 投稿数 | シェア |\n"
        md_content += "| :--- | :--- | :--- |\n"
        for h in item['heavy']:
            share = h['videoCount'] / item['total'] * 100
            md_content += f"| {h['label']} | {int(h['videoCount'])}本 | {share:.1f}% |\n"
        md_content += "\n"

    report_path = "results/explanation/heavy_creators_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    
    print(f"Graph generation complete.")
    print(f"Report saved to: {report_path}")

if __name__ == "__main__":
    main()
