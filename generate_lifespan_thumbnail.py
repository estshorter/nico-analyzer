# /// script
# dependencies = [
#   "matplotlib",
#   "matplotlib-fontja",
#   "pandas",
#   "numpy",
# ]
# ///

import pickle
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib_fontja
from pathlib import Path
from common_utils import filter_software_talk

# 日本語フォント設定
matplotlib_fontja.japanize()

def preprocess_data(category):
    pickle_path = Path(f"results/{category}.pickle")
    if not pickle_path.exists():
        return None
    with open(pickle_path, "rb") as f:
        recv = pickle.load(f)
    df = pd.json_normalize(recv["data"])
    
    if category == "software_talk":
        df = filter_software_talk(df)
    
    df["startTime"] = pd.to_datetime(df["startTime"])
    df.fillna({"userId": 0}, inplace=True)
    df["userId"] = df["userId"].astype("uint64")
    return df

def calculate_stats(df):
    df_valid = df[df["userId"] != 0]
    user_stats = df_valid.groupby("userId")["startTime"].agg(["min", "max"])
    now = df_valid["startTime"].max()
    cutoff_date = now - pd.DateOffset(years=1)
    
    # --- 生存曲線/引退率の計算 (引退済みユーザー対象) ---
    retired_users = user_stats[user_stats["max"] < cutoff_date].copy()
    if len(retired_users) == 0:
        return pd.Series(), pd.Series(), pd.Series()
        
    retired_users["lifespan"] = (retired_users["max"] - retired_users["min"]).dt.days // 365
    lifespan_counts = retired_users["lifespan"].value_counts().sort_index()
    total_retired = len(retired_users)
    
    # 累積引退率 (0年目=0%からスタート)
    cumulative_retirement = (lifespan_counts.cumsum() / total_retired) * 100
    retirement_rate = pd.concat([pd.Series([0.0], index=[-1]), cumulative_retirement])
    retirement_rate.index = retirement_rate.index + 1
    
    return retirement_rate

def main():
    # 対象カテゴリー
    categories = ["explanation", "onboard"]
    labels = {
        "software_talk": "全体", 
        "explanation": "解説", 
        "onboard": "車載"
    }
    
    colors = {
        "全体": "#FFFFFF",      # 白
        "解説": "#FFD700",      # ゴールド/黄
        "車載": "#00FF7F"       # スプリンググリーン
    }

    output_dir = Path("results/survival_analysis_no_travel")
    output_dir.mkdir(parents=True, exist_ok=True)

    all_retirement = {}

    for cat in categories:
        print(f"Processing {cat}...")
        df = preprocess_data(cat)
        if df is not None:
            r = calculate_stats(df)
            if not r.empty:
                all_retirement[labels[cat]] = r

    # サムネイル作成
    fig, ax = plt.subplots(figsize=(16, 9))
    fig.patch.set_facecolor('#000000') # 真っ黒
    ax.set_facecolor('#000000')

    # 生存率比較グラフ (1年から表示)
    for label, series in all_retirement.items():
        series_from_1 = series[series.index >= 1]
        survival_rate = 100 - series_from_1
        
        linewidth = 12 if label == "全体" else 8
        markersize = 24 if label == "全体" else 16
        zorder = 10 if label == "全体" else 5
        color = colors.get(label, "gray")
        
        import matplotlib.patheffects as path_effects
        pe = [path_effects.withStroke(linewidth=linewidth+6, foreground='black', alpha=0.3)]
        
        ax.plot(survival_rate.index, survival_rate.values, 
                marker='o', linewidth=linewidth, 
                markersize=markersize, zorder=zorder, color=color,
                path_effects=pe)

    # 装飾をすべて削除
    ax.set_title("")
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.grid(False)
    ax.set_xticks([])
    ax.set_yticks([])
    
    # 軸の設定
    ax.set_xlim(0.5, 10.5)
    ax.set_ylim(-2, 40) # 生存率（100-引退率）の範囲に合わせて調整
    
    # 枠線を消す
    for spine in ax.spines.values():
        spine.set_visible(False)

    output_path = output_dir / "lifespan_thumbnail.png"
    plt.tight_layout(pad=0)
    plt.savefig(output_path, dpi=120, facecolor='#000000', edgecolor='none')
    plt.close()

    print(f"Thumbnail saved to {output_path}")

if __name__ == "__main__":
    main()
