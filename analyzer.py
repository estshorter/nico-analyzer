import datetime
import pickle
import sys
import tomllib
import xml.etree.ElementTree as ET

import japanize_matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import requests
import seaborn as sns

# SHOW_PLOT = True
SHOW_PLOT = False


def visualize_both(df, category, title):
    print("再生数")
    df2 = df[["startTime", "viewCounter"]]
    annualView = df2.resample("Y", on="startTime").sum()
    x = list(annualView.index)
    x = [d.year for d in x]
    print(annualView)
    print("=======")
    print("投稿数")

    df2 = df["startTime"].value_counts()
    annualSubmit = df2.resample("Y").sum()
    print(annualSubmit)
    print("=======")

    # step1 グラフフレームの作成
    fig, ax = plt.subplots()

    # step2 y軸の作成
    twin1 = ax.twinx()

    # step3 折れ線グラフの描画
    (p1,) = ax.plot(x, annualSubmit, marker="o", color="C0", label="投稿数")
    (p2,) = twin1.plot(x, annualView["viewCounter"] / (10**6), color="C1", marker="o", label="再生数")

    ax.set_xlabel("投稿年")
    twin1.set_ylabel("再生数（百万単位）")
    ax.set_ylabel("投稿数")
    ax.set_title(title)

    ax.yaxis.get_label().set_color(p1.get_color())
    twin1.yaxis.get_label().set_color(p2.get_color())

    # step4 凡例の追加
    ax.legend(handles=[p1, p2])

    plt.gcf().autofmt_xdate()
    if SHOW_PLOT:
        plt.show()
    else:
        plt.savefig(f"results/{category}_annual-both.png", dpi=300, bbox_inches="tight")
    plt.close("all")


def visualize_newcomer(df: pd.DataFrame, category: str, title: str):
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
        plt.savefig(f"results/{category}_annual-newcommer.png", dpi=300, bbox_inches="tight")
    plt.close("all")


def visualize_distribution(df: pd.DataFrame, category: str, title: str, dist_ylim: str):
    df2 = df[["startTime", "viewCounter"]].copy()
    df2.loc[:, "startTime"] = df2["startTime"].apply(lambda x: x.year)
    sns.boxplot(data=df2, x="startTime", y="viewCounter")

    plt.gca().set_xlabel("投稿年")
    plt.gca().set_ylabel("再生数")
    plt.gca().set_title(title)
    plt.grid()

    plt.ylim(dist_ylim)
    plt.gcf().autofmt_xdate()
    if SHOW_PLOT:
        plt.show()
    else:
        plt.savefig(f"results/{category}_annual-distribution.png", dpi=300, bbox_inches="tight")
    plt.close("all")


def tee(msg, f):
    print(msg)
    f.write(msg)
    f.write("\n")


def show_most_popular_video(df: pd.DataFrame, category):
    print("最大再生数の動画")
    df2 = df
    with open(f"results/{category}_most_popular.csv", mode="w", encoding="utf8") as f:
        for year in range(df2["startTime"].min().year, df2["startTime"].max().year + 1):
            start = f"{year}-01-01T00:00:00+09:00"
            end = f"{year + 1}-01-01T00:00:00+09:00"
            data = df.query("startTime.between(@start, @end)")
            idxmax = data["viewCounter"].idxmax()
            popular = data.loc[idxmax, :]
            url = f'https://seiga.nicovideo.jp/api/user/info?id={popular["userId"]}'
            header = {"User-Agent": "Mozilla/5.0"}
            r = requests.get(url, headers=header)
            root = ET.fromstring(r.text)
            tee(f"{popular["startTime"]},{root.findtext("user/nickname")},{popular["title"]},{popular["viewCounter"]}", f)


def preprocess(category):
    with open(f"results/{category}.pickle", "rb") as f:
        recv = pickle.load(f)
    # print(recv["meta"])
    df = pd.json_normalize(recv["data"])
    df["startTime"] = pd.to_datetime(df["startTime"])
    df = df.sort_values("startTime", ignore_index=True)
    df.fillna({"userId": 0}, inplace=True)
    df["userId"] = df["userId"].astype("uint64")
    date = datetime.datetime.now()
    df = df[df.startTime < pd.to_datetime(f"{date.year}-01-01T00:00:00+09:00")]
    return df


def main(category, title, dist_ylim):
    df = preprocess(category)
    visualize_newcomer(df, category, title)
    visualize_both(df, category, title)
    visualize_distribution(df, category, title, dist_ylim)
    show_most_popular_video(df, category)


if __name__ == "__main__":
    args = sys.argv
    if len(args) == 2:
        with open("config.toml", "rb") as f:
            cfg = tomllib.load(f)
        main(args[1], cfg[args[1]]["title"], cfg[args[1]]["dist_ylim"])
    else:
        print("コマンドライン引数が少なすぎます")
