"""
Processing Overview:
ジャンルごとの投稿者の「生存率（継続率）」を分析・比較します。
デビュー年別の現役率（1年以内に投稿があるか）や、引退したユーザーが活動を止めるまでの期間分布（生存曲線）を算出。
ジャンルによって投稿者が定着しやすいか、短期間で離脱しやすいかの傾向を可視化します。
"""

import pickle
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib_fontja
import seaborn as sns
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

def calculate_continuation(df):
    df_valid = df[df["userId"] != 0]
    user_debut = df_valid.groupby("userId")["startTime"].min().dt.year
    now = df_valid["startTime"].max()
    cutoff_date = now - pd.DateOffset(years=1)
    active_users = set(df_valid[df_valid["startTime"] > cutoff_date]["userId"].unique())
    
    min_year = user_debut.min()
    max_year = user_debut.max()
    
    years, rates = [], []
    for y in range(max_year - 10, max_year + 1): # 直近10年分程度
        cohort_uids = user_debut[user_debut == y].index
        if len(cohort_uids) == 0: continue
        survivors = [uid for uid in cohort_uids if uid in active_users]
        rates.append((len(survivors) / len(cohort_uids)) * 100)
        years.append(y)
    return pd.Series(rates, index=years)

def calculate_lifespan(df):
    df_valid = df[df["userId"] != 0]
    user_stats = df_valid.groupby("userId")["startTime"].agg(["min", "max"])
    now = df_valid["startTime"].max()
    cutoff_date = now - pd.DateOffset(years=1)
    
    # 引退したユーザー（1年以上投稿なし）の活動期間を計算
    retired_users = user_stats[user_stats["max"] < cutoff_date].copy()
    if len(retired_users) == 0: return pd.Series()
    
    retired_users["lifespan"] = (retired_users["max"] - retired_users["min"]).dt.days // 365
    lifespan_counts = retired_users["lifespan"].value_counts().sort_index()
    
    # 累積構成比 (100% - 累積構成比 = 生存率)
    total_retired = len(retired_users)
    cumulative_dropout = (lifespan_counts.cumsum() / total_retired) * 100
    survival_rate = 100 - cumulative_dropout
    # 0年目の生存率は100%として追加
    survival_rate = pd.concat([pd.Series([100.0], index=[-1]), survival_rate])
    survival_rate.index = survival_rate.index + 1
    return survival_rate

def main():
    # biimとfishingを除外
    categories = ["software_talk", "game", "theater", "explanation", "onboard", "travel", "kitchen"]
    labels = {
        "software_talk": "全体", "game": "実況", "theater": "劇場", 
        "explanation": "解説", "onboard": "車載", "travel": "旅行", "kitchen": "キッチン"
    }
    
    output_dir = Path("results/comparison")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    continuation_results = {}
    survival_results = {}
    
    for cat in categories:
        print(f"Analyzing {cat}...")
        df = preprocess_data(cat)
        if df is not None:
            continuation_results[labels[cat]] = calculate_continuation(df)
            survival_results[labels[cat]] = calculate_lifespan(df)

    # 1. 投稿継続率の比較
    plt.figure(figsize=(12, 7))
    for label, series in continuation_results.items():
        plt.plot(series.index, series.values, marker='o', label=label, linewidth=2)
    plt.title("ジャンル別 投稿継続率比較 (デビュー年別・1年以内の投稿あり)", fontsize=16)
    plt.xlabel("デビュー年", fontsize=12)
    plt.ylabel("現役率 (%)", fontsize=12)
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.legend()
    plt.ylim(0, 100)
    plt.savefig(output_dir / "comparison_continuation.png", dpi=300)
    plt.close()

    # 2. 生存曲線の比較
    plt.figure(figsize=(12, 7))
    for label, series in survival_results.items():
        if not series.empty:
            plt.plot(series.index, series.values, marker='s', label=label, linewidth=2)
    plt.title("ジャンル別 投稿者生存曲線 (引退済みユーザーの活動期間分布)", fontsize=16)
    plt.xlabel("活動期間 (年)", fontsize=12)
    plt.ylabel("生存率 (%)", fontsize=12)
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.legend()
    plt.xlim(0, 10) # 10年程度まで表示
    plt.ylim(0, 105)
    plt.savefig(output_dir / "comparison_survival_curve.png", dpi=300)
    plt.close()

    print(f"Comparison survival plots saved to {output_dir}")

if __name__ == "__main__":
    main()
