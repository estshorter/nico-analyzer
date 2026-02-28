# /// script
# dependencies = [
#   "matplotlib",
#   "matplotlib-fontja",
#   "pandas",
#   "requests",
#   "seaborn",
# ]
# ///

import datetime
import pickle
import sys
import tomllib
import xml.etree.ElementTree as ET
from pathlib import Path

import matplotlib_fontja
import matplotlib.pyplot as plt
import pandas as pd
import requests
import seaborn as sns

from common_utils import filter_software_talk

# SHOW_PLOT = True
SHOW_PLOT = False

VIOLINPLOT = True


def visualize_both(df, category, title, output_dir):
    print("再生数")
    df2 = df[["startTime", "viewCounter"]]
    annualView = df2.resample("YE", on="startTime").sum()

    # 2025年まで表示するようにインデックスを調整
    start_dt = annualView.index.min()
    end_dt = pd.Timestamp("2025-12-31").tz_localize(start_dt.tz)
    target_index = pd.date_range(start=start_dt, end=end_dt, freq="YE")
    annualView = annualView.reindex(target_index, fill_value=0)
    x = [d.year for d in annualView.index]
    print(annualView)

    print("再生数（中央値）")
    annualViewMedian = df2.resample("YE", on="startTime").quantile(0.5).reindex(target_index, fill_value=0)
    print(annualViewMedian)
    print("=======")

    print("=======")
    print("投稿数")

    df_counts = df["startTime"].value_counts()
    annualSubmit = df_counts.resample("YE").sum().reindex(target_index, fill_value=0)
    print(annualSubmit)
    print("=======")

    # step1 グラフフレームの作成
    fig, ax = plt.subplots()

    # step2 y軸の作成
    twin1 = ax.twinx()

    # step3 折れ線グラフの描画
    p1 = ax.bar(x, annualSubmit, color="C0", label="投稿数", alpha=0.6)
    (p2,) = twin1.plot(x, annualView["viewCounter"] / (10**6), color="C1", marker="o", label="再生数")

    ax.set_xlabel("投稿年")
    twin1.set_ylabel("再生数（百万単位）")
    ax.set_ylabel("投稿数")
    ax.set_title(title)

    # ax.yaxis.get_label().set_color(p1.get_color())
    ax.yaxis.label.set_color("C0")
    twin1.yaxis.get_label().set_color(p2.get_color())

    # step4 凡例の追加
    ax.legend(handles=[p1, p2])

    ax.grid(axis='x', linestyle=":", alpha=0.6)

    plt.gcf().autofmt_xdate()
    if SHOW_PLOT:
        plt.show()
    else:
        plt.savefig(output_dir / f"{category}_annual-both.png", dpi=300, bbox_inches="tight")
    plt.close("all")


def visualize_newcomer(df: pd.DataFrame, category: str, title: str, output_dir):
    df2 = df.groupby("userId").min()
    newcommers = {}
    for d in df2["startTime"]:
        current = newcommers.get(d.year, 0)
        newcommers[d.year] = current + 1
    newcommers_list = sorted(newcommers.items())
    print("新規投稿者数")
    print("year, count")
    for year, count in newcommers_list:
        print(f"{year}, {count:5d}")
    print("=======")
    x = list(range(newcommers_list[0][0], newcommers_list[-1][0] + 1))
    y = [newcommers.get(x_, 0) for x_ in x]

    # step3 折れ線グラフの描画
    (p1,) = plt.plot(x, y, marker="o", color="C0", label="新規投稿者数")
    plt.gca().set_xlabel("投稿年")
    plt.gca().set_ylabel("新規投稿者数")
    plt.gca().set_title(title)

    plt.gca().yaxis.get_label().set_color(p1.get_color())
    plt.grid()
    plt.gcf().autofmt_xdate()
    if SHOW_PLOT:
        plt.show()
    else:
        plt.savefig(output_dir / f"{category}_annual-newcommer.png", dpi=300, bbox_inches="tight")
    plt.close("all")


def visualize_distribution(df: pd.DataFrame, category: str, title: str, dist_ylim: str, output_dir):
    df2 = df[["startTime", "viewCounter"]].copy()
    df2["startTime"] = df2["startTime"].dt.year
    if VIOLINPLOT:
        sns.violinplot(data=df2.query("startTime >= 2018"), x="startTime", y="viewCounter", cut=0, width=0.5)
    else:
        sns.boxplot(data=df2.query("startTime >= 2018"), x="startTime", y="viewCounter")

    plt.gca().set_xlabel("投稿年")
    plt.gca().set_ylabel("再生数")
    plt.gca().set_title(title)
    plt.grid()
 
    plt.ylim(dist_ylim)
    plt.gcf().autofmt_xdate()
    if SHOW_PLOT:
        plt.show()
    else:
        plt.savefig(output_dir / f"{category}_annual-distribution.png", dpi=300, bbox_inches="tight")
    plt.close("all")


def tee(msg, f):
    print(msg)
    f.write(msg)
    f.write("\n")


def show_most_popular_video(df: pd.DataFrame, category, output_dir):
    print("最大再生数の動画")
    df2 = df
    with open(output_dir / f"{category}_most_popular.csv", mode="w", encoding="utf8") as f:
        for year in range(df2["startTime"].min().year, df2["startTime"].max().year + 1):
            start = f"{year}-01-01T00:00:00+09:00"
            end = f"{year + 1}-01-01T00:00:00+09:00"
            data = df.query("startTime.between(@start, @end)")
            if len(data) == 0:
                continue
            idxmax = data["viewCounter"].idxmax()
            popular = data.loc[idxmax, :]
            url = f'https://seiga.nicovideo.jp/api/user/info?id={popular["userId"]}'
            header = {"User-Agent": "Mozilla/5.0"}
            r = requests.get(url, headers=header)
            root = ET.fromstring(r.text)
            tee(f"{popular["startTime"]},{root.findtext("user/nickname")},{popular["title"]},{popular["viewCounter"]}", f)


def visualize_continuation(df: pd.DataFrame, category: str, title: str, output_dir):
    print("投稿継続分析 (デビュー年別)")
    df_valid = df[df["userId"] != 0]

    # Determine Debut Year for each user
    user_debut = df_valid.groupby("userId")["startTime"].min().dt.year

    # Determine active users (posted within last 1 year from max date)
    now = df_valid["startTime"].max()
    cutoff_date = now - pd.DateOffset(years=1)
    
    print(f"Reference date: {now.date()}")
    print(f"Active criteria: Posted after {cutoff_date.date()}")

    active_users = set(df_valid[df_valid["startTime"] > cutoff_date]["userId"].unique())

    # Range of debut years
    min_year = user_debut.min()
    max_year = user_debut.max()

    years = []
    counts = []
    rates = []

    print("Debut Year, Total Debuts, Active(>1yr), Rate(%)")

    for y in range(min_year, max_year + 1):
        # Users who debuted in year y
        cohort_uids = user_debut[user_debut == y].index
        total_cohort = len(cohort_uids)

        if total_cohort == 0:
            continue

        # How many of them are in active_users?
        survivors = [uid for uid in cohort_uids if uid in active_users]
        count = len(survivors)
        rate = (count / total_cohort) * 100

        years.append(y)
        counts.append(count)
        rates.append(rate)
        print(f"{y}, {total_cohort}, {count}, {rate:.2f}%")

    print("=======")
    
    # Plot
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()

    # Plot Count on ax1 (Bar)
    p1 = ax1.bar(years, counts, color="C0", label="現役投稿者数", alpha=0.6)

    # Plot Rate on ax2 (Line)
    (p2,) = ax2.plot(years, rates, marker="o", color="C1", label="投稿継続率")

    # Set labels and title
    ax1.set_xlabel("デビュー年")
    ax1.set_ylabel("現役投稿者数")
    ax2.set_ylabel("投稿継続率 (%)")
    ax1.set_title(f"{title} (投稿継続状況)")

    # Color axes
    ax1.yaxis.label.set_color("C0")
    # ax1.tick_params(axis='y', colors="C0")
    
    ax2.yaxis.label.set_color("C1")
    # ax2.tick_params(axis='y', colors="C1")

    # Grid
    # ax1.grid(axis='x')
    ax1.grid(axis='x', linestyle=":", alpha=0.6)
    # ax2.grid(axis='y')

    # Legend
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc="upper left")

    plt.gcf().autofmt_xdate()

    if SHOW_PLOT:
        plt.show()
    else:
        plt.savefig(output_dir / f"{category}_continuation.png", dpi=300, bbox_inches="tight")
    plt.close("all")


def visualize_lifespan(df: pd.DataFrame, category: str, title: str, output_dir):
    print("投稿者寿命分析")
    df_valid = df[df["userId"] != 0]

    # User stats
    user_stats = df_valid.groupby("userId")["startTime"].agg(["min", "max"])

    # Determine cutoff (1 year ago from the last recorded post in dataset)
    # Use the max date in the data as "now" to ensure reproducibility
    now = df_valid["startTime"].max()
    cutoff_date = now - pd.DateOffset(years=1)
    
    print(f"Reference date (Latest post): {now.date()}")
    print(f"Cutoff date (Active within 1 year): {cutoff_date.date()}")

    # Filter: Keep users whose last post is OLDER than cutoff_date
    retired_users = user_stats[user_stats["max"] < cutoff_date].copy()

    print(f"Total users: {len(user_stats)}")
    print(f"Retired users (Last post before {cutoff_date.date()}): {len(retired_users)}")

    # Calculate lifespan in years (floor)
    retired_users["lifespan"] = (retired_users["max"] - retired_users["min"]).dt.days // 365

    # Count frequency of each lifespan
    lifespan_counts = retired_users["lifespan"].value_counts().sort_index()
    
    # Fill missing years with 0
    if not lifespan_counts.empty:
        full_range = range(int(lifespan_counts.index.min()), int(lifespan_counts.index.max()) + 1)
        lifespan_counts = lifespan_counts.reindex(full_range, fill_value=0)

    print("Lifespan (Years), Count")
    for yrs, count in lifespan_counts.items():
        print(f"{yrs}, {count}")

    print("=======")

    # Plot
    fig, ax = plt.subplots()

    # Bar chart
    ax.bar(lifespan_counts.index, lifespan_counts.values, color="C0", label="人数", alpha=0.6)

    ax.set_xlabel("活動期間 (年)")
    ax.set_ylabel("人数")
    ax.yaxis.label.set_color("C0")
    ax.set_title("投稿者寿命分布")
    # ax.set_title(f"{title} (投稿者寿命分布)")
    ax.grid(axis='y')
    ax.grid(axis='x', linestyle=":", alpha=0.6)

    # Fix x-axis ticks to be integers
    if not lifespan_counts.empty:
        ax.set_xticks(range(int(lifespan_counts.index.max()) + 1))

        # Add percentage axis & Plot Line
        ax2 = ax.twinx()
        total_retired = len(retired_users)
        
        # Calculate Cumulative Percentage (Cumulative Dropout Rate)
        cumulative_percentages = (lifespan_counts.cumsum() / total_retired) * 100
        print(cumulative_percentages)
        
        (p2,) = ax2.plot(cumulative_percentages.index, cumulative_percentages.values, color="C1", marker="o", label="累積構成比")
        
        ax2.set_ylabel("累積構成比 (%)")
        ax2.yaxis.label.set_color("C1")
        
        # Combine legends
        lines, labels = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2, loc="lower right")

    if SHOW_PLOT:
        plt.show()
    else:
        plt.savefig(output_dir / f"{category}_lifespan.png", dpi=300, bbox_inches="tight")
    plt.close("all")


def visualize_lifespan_thumbnail(df: pd.DataFrame, category: str, title: str, output_dir):
    print("投稿者寿命分析 (サムネイル・文字なし)")
    df_valid = df[df["userId"] != 0]

    # User stats
    user_stats = df_valid.groupby("userId")["startTime"].agg(["min", "max"])

    # Determine cutoff (1 year ago from the last recorded post in dataset)
    now = df_valid["startTime"].max()
    cutoff_date = now - pd.DateOffset(years=1)
    
    # Filter: Keep users whose last post is OLDER than cutoff_date
    retired_users = user_stats[user_stats["max"] < cutoff_date].copy()

    # Calculate lifespan in years (floor)
    retired_users["lifespan"] = (retired_users["max"] - retired_users["min"]).dt.days // 365

    # Count frequency of each lifespan
    lifespan_counts = retired_users["lifespan"].value_counts().sort_index()
    
    # Fill missing years with 0
    if not lifespan_counts.empty:
        full_range = range(int(lifespan_counts.index.min()), int(lifespan_counts.index.max()) + 1)
        lifespan_counts = lifespan_counts.reindex(full_range, fill_value=0)

    # Plot
    with plt.style.context("dark_background"):
        fig, ax = plt.subplots()

        # Bar chart
        ax.bar(lifespan_counts.index, lifespan_counts.values, color="C0", alpha=0.6)

        # Remove labels and title
        # ax.set_xlabel("活動期間 (年)")
        # ax.set_ylabel("人数")
        # ax.set_title("投稿者寿命分布 (生存率)")
        
        # Completely hide y-axis (ticks, labels, spines associated with y)
        ax.yaxis.set_visible(False)
        
        # Manually hide spines just in case set_visible(False) doesn't cover everything in this style
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['left'].set_color('none') # Ensure it's invisible
        ax.spines['bottom'].set_visible(True)

        # Remove x-axis tick marks and labels, but keep the axis line (spine)
        ax.tick_params(labelbottom=False, bottom=False)

        # Fix x-axis ticks to be integers
        if not lifespan_counts.empty:
            ax.set_xticks(range(int(lifespan_counts.index.max()) + 1))

            # Add percentage axis & Plot Line
            ax2 = ax.twinx()
            total_retired = len(retired_users)
            
            # Calculate Survival Rate
            cumulative_percentages = (lifespan_counts.cumsum() / total_retired) * 100
            survival_rate = 100 - cumulative_percentages
            
            ax2.plot(survival_rate.index, survival_rate.values, color="C1", marker="o", linewidth=3)
            
            ax2.set_ylim(0, 100)
            
            # Completely hide secondary y-axis
            ax2.yaxis.set_visible(False)
            ax2.spines['top'].set_visible(False)
            ax2.spines['right'].set_visible(False)
            ax2.spines['left'].set_visible(False)
            ax2.spines['bottom'].set_visible(False)

            # No legend needed for thumbnail background
            # lines, labels = ax.get_legend_handles_labels()
            # lines2, labels2 = ax2.get_legend_handles_labels()
            # ax2.legend(lines + lines2, labels + labels2, loc="upper right")

        if SHOW_PLOT:
            plt.show()
        else:
            plt.savefig(output_dir / f"{category}_lifespan_thumbnail.png", dpi=300, bbox_inches="tight", transparent=False)
        plt.close("all")


def preprocess(category):
    with open(f"results/{category}.pickle", "rb") as f:
        recv = pickle.load(f)
    # print(recv["meta"])
    df = pd.json_normalize(recv["data"])

    # ソフトウェアトークの場合、VOCALOID関連を除外（歌唱系が混じるため）
    if category == "software_talk":
        df = filter_software_talk(df)

    df["startTime"] = pd.to_datetime(df["startTime"])
    df = df.sort_values("startTime", ignore_index=True)
    df.fillna({"userId": 0}, inplace=True)
    df["userId"] = df["userId"].astype("uint64")
    date = datetime.datetime.now()
    # df = df[df.startTime < pd.to_datetime(f"{date.year}-01-01T00:00:00+09:00")]
    return df


def main(category, title, dist_ylim):
    output_dir = Path("results") / category
    output_dir.mkdir(parents=True, exist_ok=True)
    
    df = preprocess(category)
    visualize_newcomer(df, category, title, output_dir)
    visualize_both(df, category, title, output_dir)
    visualize_distribution(df, category, title, dist_ylim, output_dir)
    visualize_continuation(df, category, title, output_dir)
    show_most_popular_video(df, category, output_dir)
    visualize_lifespan(df, category, title, output_dir)
    # visualize_lifespan_thumbnail(df, category, title, output_dir)


if __name__ == "__main__":
    args = sys.argv
    if len(args) == 2:
        with open("config.toml", "rb") as f:
            cfg = tomllib.load(f)
        main(args[1], cfg[args[1]]["title"], cfg[args[1]]["dist_ylim"])
    else:
        print("コマンドライン引数が少なすぎます")
