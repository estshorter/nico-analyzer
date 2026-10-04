
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
    
    # 生存率 (100% - 引退率)
    survival_rate = 100 - retirement_rate

    # --- 投稿継続率の計算 (デビュー年別) ---
    user_debut = df_valid.groupby("userId")["startTime"].min().dt.year
    active_users = set(df_valid[df_valid["startTime"] > cutoff_date]["userId"].unique())
    
    # 2026年を除外（2025年までを表示）
    max_year = 2025
    years, cont_rates = [], []
    for y in range(max_year - 9, max_year + 1): # 直近10年分
        cohort_uids = user_debut[user_debut == y].index
        if len(cohort_uids) == 0: continue
        survivors = [uid for uid in cohort_uids if uid in active_users]
        cont_rates.append((len(survivors) / len(cohort_uids)) * 100)
        years.append(y)
    continuation_rate = pd.Series(cont_rates, index=years)

    return survival_rate, retirement_rate, continuation_rate

def main():
    # 旅行を除外するバージョン
    categories = ["software_talk", "game", "theater", "explanation", "kitchen", "onboard"]
    labels = {
        "software_talk": "全体", "explanation": "解説", "kitchen": "キッチン", 
        "onboard": "車載", "game": "実況", "theater": "劇場"
    }

    output_dir = Path("results/survival_analysis_no_travel")
    output_dir.mkdir(parents=True, exist_ok=True)

    all_survival = {}
    all_retirement = {}
    all_continuation = {}

    for cat in categories:
        print(f"Processing {cat}...")
        df = preprocess_data(cat)
        if df is not None:
            s, r, c = calculate_stats(df)
            if not s.empty:
                all_survival[labels[cat]] = s
                all_retirement[labels[cat]] = r
                all_continuation[labels[cat]] = c

    # 1. 生存率比較グラフ (0年から表示)
    plt.figure(figsize=(12, 7))
    for label, series in all_survival.items():
        linewidth = 4 if label == "全体" else 2
        markersize = 10 if label == "全体" else 6
        zorder = 10 if label == "全体" else 11 if label == "劇場" else 5
        plt.plot(series.index, series.values, marker='s', label=label, linewidth=linewidth, markersize=markersize, zorder=zorder)
    plt.title("ジャンル別 投稿者生存曲線 (活動期間別)", fontsize=22)
    plt.xlabel("活動期間 (年)", fontsize=18)
    plt.ylabel("生存率 (%)", fontsize=18)
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.xticks(range(0, 11), fontsize=14)
    plt.yticks(fontsize=14)
    plt.legend(fontsize=14)
    plt.xlim(0, 10)
    plt.ylim(0, 105)
    plt.savefig(output_dir / "comparison_survival_rate.png", dpi=300)
    plt.close()

    # 2-A. 引退率比較グラフ (0年から表示：衝撃重視)
    plt.figure(figsize=(12, 7))
    for label, series in all_retirement.items():
        linewidth = 4 if label == "全体" else 2
        markersize = 10 if label == "全体" else 6
        zorder = 10 if label == "全体" else 11 if label == "劇場" else 5
        plt.plot(series.index, series.values, marker='o', label=label, linewidth=linewidth, markersize=markersize, zorder=zorder)
    plt.title("ジャンル別 投稿者累積引退率 (0年目から表示)", fontsize=22)
    plt.xlabel("活動期間 (年)", fontsize=18)
    plt.ylabel("引退率 (%)", fontsize=18)
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.xticks(range(0, 11), fontsize=14)
    plt.yticks(fontsize=14)
    plt.legend(fontsize=14)
    plt.xlim(0, 10)
    plt.ylim(0, 105)
    plt.savefig(output_dir / "comparison_retirement_rate_from_0.png", dpi=300)
    plt.close()

    # 2-B. 引退率比較グラフ (1年から表示：各年の比較重視)
    plt.figure(figsize=(12, 7))
    for label, series in all_retirement.items():
        series_from_1 = series[series.index >= 1]
        linewidth = 4 if label == "全体" else 2
        markersize = 10 if label == "全体" else 6
        zorder = 10 if label == "全体" else 11 if label == "劇場" else 5
        plt.plot(series_from_1.index, series_from_1.values, marker='o', label=label, linewidth=linewidth, markersize=markersize, zorder=zorder)
    plt.title("ジャンル別 投稿者累積引退率 (1年目以降)", fontsize=22)
    plt.xlabel("活動期間 (年)", fontsize=18)
    plt.ylabel("引退率 (%)", fontsize=18)
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.xticks(range(1, 11), fontsize=14)
    plt.yticks(fontsize=14)
    plt.legend(fontsize=14)
    plt.xlim(0.5, 10)
    plt.ylim(60, 105)
    plt.savefig(output_dir / "comparison_retirement_rate_from_1.png", dpi=300)
    plt.close()

    # 3. 継続率比較グラフ (デビュー年別)
    plt.figure(figsize=(12, 7))
    for label, series in all_continuation.items():
        linewidth = 4 if label == "全体" else 2
        markersize = 10 if label == "全体" else 6
        zorder = 10 if label == "全体" else 11 if label == "劇場" else 5
        plt.plot(series.index, series.values, marker='o', label=label, linewidth=linewidth, markersize=markersize, zorder=zorder)
    plt.title("ジャンル別 デビュー年別投稿継続率 (現役率)", fontsize=22)
    plt.xlabel("デビュー年", fontsize=18)
    plt.ylabel("現役率 (%)", fontsize=18)
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.xticks(all_continuation["全体"].index, fontsize=14)
    plt.yticks(fontsize=14)
    plt.legend(fontsize=14)
    plt.ylim(0, 105)
    plt.savefig(output_dir / "comparison_continuation_rate.png", dpi=300)
    plt.close()

    print(f"Comparison graphs saved to {output_dir}")

if __name__ == "__main__":
    main()
