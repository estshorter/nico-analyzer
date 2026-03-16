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

def get_user_counts(df):
    df_valid = df[df["userId"] != 0]
    user_stats = df_valid.groupby("userId")["startTime"].agg(["min", "max"])
    
    now = df_valid["startTime"].max()
    cutoff_date = now - pd.DateOffset(years=1)
    
    active_users = user_stats[user_stats["max"] >= cutoff_date]
    retired_users = user_stats[user_stats["max"] < cutoff_date]
    
    return len(active_users), len(retired_users)

def main():
    categories = ["software_talk", "game", "theater", "explanation", "kitchen", "onboard", "travel"]
    labels = {
        "software_talk": "全体", "explanation": "解説", "kitchen": "キッチン", 
        "onboard": "車載", "travel": "旅行", "game": "実況", "theater": "劇場"
    }

    results = []
    print(f"{'ジャンル':<10} | {'全ユーザー':<8} | {'現役':<8} | {'引退':<8} | {'現役率':<5}")
    print("-" * 55)

    for cat in categories:
        df = preprocess_data(cat)
        if df is not None:
            active, retired = get_user_counts(df)
            total = active + retired
            rate = (active / total * 100) if total > 0 else 0
            print(f"{labels[cat]:<10} | {total:<10,d} | {active:<10,d} | {retired:<10,d} | {rate:>.1f}%")
            results.append({"label": labels[cat], "rate": rate, "active": active})

    if not results:
        return

    # グラフ描画
    df_res = pd.DataFrame(results)
    plt.figure(figsize=(12, 7))
    bars = plt.bar(df_res["label"], df_res["rate"], color="gray", alpha=0.6)
    
    # 特定のカテゴリを強調
    for i, row in df_res.iterrows():
        if row["label"] == "全体":
            bars[i].set_color("tab:blue")
            bars[i].set_alpha(1.0)
        elif row["label"] == "旅行":
            bars[i].set_color("tab:pink")
            bars[i].set_alpha(1.0)

    plt.title("ジャンル別 投稿者現役率 (直近1年に投稿あり)", fontsize=22)
    plt.xlabel("ジャンル", fontsize=18)
    plt.ylabel("現役率 (%)", fontsize=18)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.ylim(0, max(df_res["rate"]) * 1.3)
    plt.gca().set_axisbelow(True)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # 数値を表示
    for i, bar in enumerate(bars):
        height = bar.get_height()
        active_count = results[i]["active"]
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                 f'{height:.1f}%\n({active_count:,d}人)', ha='center', va='bottom', fontsize=12, fontweight='bold')

    output_dir = Path("results/survival_analysis")
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_dir / "comparison_active_rate.png", dpi=300)
    plt.close()
    print(f"\nBar chart saved to {output_dir / 'comparison_active_rate.png'}")

if __name__ == "__main__":
    main()
