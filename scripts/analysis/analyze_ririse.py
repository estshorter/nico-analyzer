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

from pathlib import Path
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib_fontja
import seaborn as sns

# 日本語フォント設定
matplotlib_fontja.japanize()

# スタイル設定
sns.set_theme(style="whitegrid", font="sans-serif")
plt.rcParams["font.sans-serif"] = ["IPAGothic", "Noto Sans CJK JP", "Meiryo", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False

VOCALO_PATTERN = r"VOCALOID|VOCAROID|音楽|歌うボイスロイド|カバー曲|歌ってみた|SynthesizerV"
OUTPUT_DIR = Path("results/ririse_charts")
REPORT_PATH = Path("results/ririse_analysis_report.md")

# ジャンル定義用パターン
GENRE_PATTERNS = {
    "実況": r"実況",
    "解説": r"解説",
    "劇場": r"劇場",
    "ラジオ": r"ラジオ|雑談",
    "ASMR": r"ASMR|ASMROID|バイノーラル|耳かき",
    "車載": r"車載",
    "旅行": r"旅行|岐阜県|広島県|山口県|観光スポット|神社巡り|寺巡り|日本の風景",
    "キッチン": r"キッチン",
}
GENRE_ORDER = ["ボカロ", "実況", "解説", "劇場", "ラジオ", "ASMR", "車載", "旅行", "キッチン", "その他ボイロ"]


def load_and_preprocess_data(pickle_path: str = "results/ririse.pickle") -> pd.DataFrame:
    with open(pickle_path, "rb") as f:
        recv = pickle.load(f)
    df = pd.json_normalize(recv["data"])

    # 日時変換
    df["startTime"] = pd.to_datetime(df["startTime"])
    df["year"] = df["startTime"].dt.year
    df["date"] = df["startTime"].dt.date

    # 数値列の型変換
    df["viewCounter"] = pd.to_numeric(df["viewCounter"], errors="coerce").fillna(0).astype(int)
    df["likeCounter"] = pd.to_numeric(df["likeCounter"], errors="coerce").fillna(0).astype(int)
    df["lengthSeconds"] = pd.to_numeric(df["lengthSeconds"], errors="coerce").fillna(0).astype(int)
    df["tags"] = df["tags"].fillna("")
    df["contentType"] = df["contentType"].fillna("unknown")

    # ボカロ分類フラグ
    df["is_vocalo"] = df["tags"].str.contains(VOCALO_PATTERN, case=False, regex=True)
    df["category"] = np.where(df["is_vocalo"], "ボカロ系", "ボイロ系")

    # 期間制限フィルタ:
    # ボイロ系: 2022年以降 (VOICEPEAK 彩澄りりせ発売以降)
    # ボカロ系: 2025年以降 (Synthesizer V 2 AI 彩澄りりせ発売以降)
    df = df[
        ((~df["is_vocalo"]) & (df["year"] >= 2022)) |
        ((df["is_vocalo"]) & (df["year"] >= 2025))
    ].copy()

    # ボイロ系のジャンル判定
    for g, pat in GENRE_PATTERNS.items():
        df[f"genre_{g}"] = (~df["is_vocalo"]) & df["tags"].str.contains(pat, case=False, regex=True)

    return df


def calculate_2026_projection(df: pd.DataFrame):
    """2026年の経過日数から年間着地予測値を算出"""
    df_2026 = df[df["year"] == 2026]
    if len(df_2026) == 0:
        return None

    latest_date = df_2026["startTime"].max()
    start_of_year = pd.Timestamp("2026-01-01 00:00:00+0900")
    elapsed_days = (latest_date - start_of_year).total_seconds() / 86400.0
    annual_factor = 365.0 / elapsed_days

    df_2025 = df[df["year"] == 2025]
    total_2025 = len(df_2025)
    voiro_2025 = len(df_2025[~df_2025["is_vocalo"]])
    vocalo_2025 = len(df_2025[df_2025["is_vocalo"]])

    total_2026_act = len(df_2026)
    voiro_2026_act = int((~df_2026["is_vocalo"]).sum())
    vocalo_2026_act = int(df_2026["is_vocalo"].sum())

    total_proj = int(round(total_2026_act * annual_factor))
    voiro_proj = int(round(voiro_2026_act * annual_factor))
    vocalo_proj = int(round(vocalo_2026_act * annual_factor))

    # ジャンル別予測
    genre_proj_list = []
    voiro_2026_sub = df_2026[~df_2026["is_vocalo"]]
    voiro_2025_sub = df_2025[~df_2025["is_vocalo"]]

    # ボカロ
    voc_2025 = len(df_2025[df_2025["is_vocalo"]])
    voc_2026_act = len(df_2026[df_2026["is_vocalo"]])
    voc_proj = int(round(voc_2026_act * annual_factor))
    voc_yoy = ((voc_proj / voc_2025) - 1.0) * 100 if voc_2025 > 0 else None
    genre_proj_list.append({
        "ジャンル": "ボカロ",
        "2025年実績": voc_2025,
        "2026年実績(8/15時点)": voc_2026_act,
        "2026年着地予測": voc_proj,
        "前年比(YoY)": f"{voc_yoy:+.1f}%" if voc_yoy is not None else "-",
    })

    has_any_cols = [f"genre_{g}" for g in GENRE_PATTERNS.keys()]
    for g in GENRE_PATTERNS.keys():
        act_2025 = int(voiro_2025_sub[f"genre_{g}"].sum())
        act_2026 = int(voiro_2026_sub[f"genre_{g}"].sum())
        proj = int(round(act_2026 * annual_factor))
        yoy = ((proj / act_2025) - 1.0) * 100 if act_2025 > 0 else None
        genre_proj_list.append({
            "ジャンル": g,
            "2025年実績": act_2025,
            "2026年実績(8/15時点)": act_2026,
            "2026年着地予測": proj,
            "前年比(YoY)": f"{yoy:+.1f}%" if yoy is not None else "-",
        })

    # その他ボイロ
    if len(voiro_2025_sub) > 0:
        other_2025 = int((~voiro_2025_sub[has_any_cols].any(axis=1)).sum())
    else:
        other_2025 = 0
    if len(voiro_2026_sub) > 0:
        other_2026 = int((~voiro_2026_sub[has_any_cols].any(axis=1)).sum())
    else:
        other_2026 = 0
        
    other_proj = int(round(other_2026 * annual_factor))
    other_yoy = ((other_proj / other_2025) - 1.0) * 100 if other_2025 > 0 else None
    genre_proj_list.append({
        "ジャンル": "その他ボイロ",
        "2025年実績": other_2025,
        "2026年実績(8/15時点)": other_2026,
        "2026年着地予測": other_proj,
        "前年比(YoY)": f"{other_yoy:+.1f}%" if other_yoy is not None else "-",
    })

    # 合計
    total_yoy = ((total_proj / total_2025) - 1.0) * 100 if total_2025 > 0 else None
    genre_proj_list.append({
        "ジャンル": "全体合計",
        "2025年実績": total_2025,
        "2026年実績(8/15時点)": total_2026_act,
        "2026年着地予測": total_proj,
        "前年比(YoY)": f"{total_yoy:+.1f}%" if total_yoy is not None else "-",
    })

    proj_df = pd.DataFrame(genre_proj_list)

    summary = {
        "latest_date": str(latest_date),
        "elapsed_days": elapsed_days,
        "progress_rate": (elapsed_days / 365.0) * 100,
        "annual_factor": annual_factor,
        "total_2025": total_2025,
        "total_2026_act": total_2026_act,
        "total_proj": total_proj,
        "total_yoy": total_yoy,
        "voiro_2025": voiro_2025,
        "voiro_2026_act": voiro_2026_act,
        "voiro_proj": voiro_proj,
        "voiro_yoy": ((voiro_proj / voiro_2025) - 1.0) * 100 if voiro_2025 > 0 else None,
        "vocalo_2025": vocalo_2025,
        "vocalo_2026_act": vocalo_2026_act,
        "vocalo_proj": vocalo_proj,
        "vocalo_yoy": voc_yoy,
        "proj_df": proj_df,
    }
    return summary


def analyze_yearly_stats(df: pd.DataFrame):
    """1. 投稿数、投稿者数、再生数、いいね数の各年ごとの分析"""
    yearly_all = df.groupby("year").agg(
        投稿数=("contentId", "count"),
        投稿者数=("userId", "nunique"),
        再生数合計=("viewCounter", "sum"),
        再生数中央値=("viewCounter", "median"),
        再生数平均=("viewCounter", "mean"),
        いいね合計=("likeCounter", "sum"),
        いいね中央値=("likeCounter", "median"),
        いいね平均=("likeCounter", "mean"),
    ).reset_index()

    yearly_cat = df.groupby(["year", "category"]).agg(
        投稿数=("contentId", "count"),
        投稿者数=("userId", "nunique"),
        再生数合計=("viewCounter", "sum"),
        再生数中央値=("viewCounter", "median"),
        再生数平均=("viewCounter", "mean"),
        いいね合計=("likeCounter", "sum"),
        いいね中央値=("likeCounter", "median"),
        いいね平均=("likeCounter", "mean"),
    ).reset_index()

    return yearly_all, yearly_cat


def analyze_genre_stats(df: pd.DataFrame):
    """2. ジャンル別投稿数の各年ごとの分析"""
    years = sorted(df["year"].unique())
    genre_flag_data = []
    has_any_cols = [f"genre_{g}" for g in GENRE_PATTERNS.keys()]

    for y in years:
        sub = df[df["year"] == y]
        vocalo_count = int(sub["is_vocalo"].sum())
        voiro_sub = sub[~sub["is_vocalo"]]
        
        row = {
            "年": y,
            "ボカロ": vocalo_count,
        }
        for g in GENRE_PATTERNS.keys():
            row[g] = int(voiro_sub[f"genre_{g}"].sum())
        
        if len(voiro_sub) > 0:
            has_any = voiro_sub[has_any_cols].any(axis=1)
            row["その他ボイロ"] = int((~has_any).sum())
        else:
            row["その他ボイロ"] = 0
            
        row["ボイロ系実動画数"] = len(voiro_sub)
        row["全体実動画数"] = len(sub)

        genre_flag_data.append(row)

    genre_df = pd.DataFrame(genre_flag_data)
    return genre_df


def analyze_short_ratio(df: pd.DataFrame):
    """3. 投稿数のショート・ロング比率（2026/4/15以降）"""
    cutoff_time = pd.Timestamp("2026-04-15 00:00:00+0900")
    recent_df = df[df["startTime"] >= cutoff_time].copy()

    total_recent = len(recent_df)
    short_count = int((recent_df["contentType"] == "short").sum())
    long_count = int((recent_df["contentType"] == "long").sum())
    other_count = total_recent - short_count - long_count

    short_ratio = (short_count / total_recent * 100) if total_recent > 0 else 0.0
    long_ratio = (long_count / total_recent * 100) if total_recent > 0 else 0.0

    breakdown = recent_df.groupby(["category", "contentType"]).agg(
        投稿数=("contentId", "count"),
        再生数中央値=("viewCounter", "median"),
        再生数平均=("viewCounter", "mean"),
        いいね中央値=("likeCounter", "median"),
        いいね平均=("likeCounter", "mean"),
        平均動画尺_秒=("lengthSeconds", "mean"),
    ).reset_index()

    summary = {
        "cutoff_time": str(cutoff_time),
        "total_recent": total_recent,
        "short_count": short_count,
        "short_ratio": short_ratio,
        "long_count": long_count,
        "long_ratio": long_ratio,
        "other_count": other_count,
        "breakdown": breakdown,
        "recent_df": recent_df,
    }
    return summary


def plot_visualizations(df: pd.DataFrame, yearly_all: pd.DataFrame, yearly_cat: pd.DataFrame, genre_df: pd.DataFrame, short_summary: dict, proj_summary: dict):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    colors = {
        "ボイロ系": "#2b5c8f",
        "ボカロ系": "#e74c3c",
        "ボカロ": "#e74c3c",
        "実況": "#3498db",
        "解説": "#1abc9c",
        "劇場": "#9b59b6",
        "ラジオ": "#f39c12",
        "ASMR": "#e84393",
        "車載": "#e67e22",
        "旅行": "#2ecc71",
        "キッチン": "#f1c40f",
        "その他ボイロ": "#7f8c8d",
        "long": "#2980b9",
        "short": "#e74c3c",
    }

    all_years = sorted(df["year"].unique())

    # -------------------------------------------------------------
    # Chart 1: 投稿数 & 投稿者数の年次推移 (ボカロ vs ボイロ) + 2026予測
    # -------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.2))
    
    pivot_posts = yearly_cat.pivot(index="year", columns="category", values="投稿数").fillna(0)
    for c in ["ボイロ系", "ボカロ系"]:
        if c not in pivot_posts.columns:
            pivot_posts[c] = 0
    pivot_posts = pivot_posts[["ボイロ系", "ボカロ系"]]

    posts_with_proj = pivot_posts.copy()
    posts_with_proj.loc["2026予測"] = [proj_summary["voiro_proj"], proj_summary["vocalo_proj"]]

    posts_with_proj.plot(kind="bar", stacked=True, ax=axes[0], color=[colors["ボイロ系"], colors["ボカロ系"]], width=0.55, edgecolor="white", rot=0)
    axes[0].set_title("年別 投稿数推移 & 2026年着地予測", fontsize=13, fontweight="bold", pad=12)
    axes[0].set_xlabel("年", fontsize=11)
    axes[0].set_ylabel("投稿本数 (本)", fontsize=11)
    axes[0].grid(axis="y", linestyle="--", alpha=0.7)
    axes[0].legend(title="カテゴリ")
    for c in axes[0].containers:
        for p in c:
            val = int(p.get_height())
            if val > 15:
                axes[0].annotate(f"{val}", (p.get_x() + p.get_width() / 2, p.get_y() + val / 2),
                                ha="center", va="center", color="white", fontweight="bold", fontsize=9)

    pivot_users = yearly_cat.pivot(index="year", columns="category", values="投稿者数").fillna(0)
    for c in ["ボイロ系", "ボカロ系"]:
        if c not in pivot_users.columns:
            pivot_users[c] = 0
    pivot_users = pivot_users[["ボイロ系", "ボカロ系"]]
    pivot_users.plot(kind="bar", ax=axes[1], color=[colors["ボイロ系"], colors["ボカロ系"]], width=0.6, edgecolor="white", rot=0)
    axes[1].set_title("年別 投稿者数推移（ユニーク投稿者）", fontsize=13, fontweight="bold", pad=12)
    axes[1].set_xlabel("年", fontsize=11)
    axes[1].set_ylabel("投稿者数 (人)", fontsize=11)
    axes[1].grid(axis="y", linestyle="--", alpha=0.7)
    axes[1].legend(title="カテゴリ")
    for c in axes[1].containers:
        for p in c:
            val = int(p.get_height())
            if val > 0:
                axes[1].annotate(f"{val}", (p.get_x() + p.get_width() / 2, val + 2),
                                ha="center", va="bottom", color="#333", fontsize=9)

    plt.tight_layout()
    p1 = OUTPUT_DIR / "01_ririse_posts_and_users.png"
    plt.savefig(p1, dpi=300)
    plt.close()
    print(f"Saved: {p1}")

    # -------------------------------------------------------------
    # Chart 2: 再生数 & いいね数（合計 & 中央値）
    # -------------------------------------------------------------
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))

    pivot_views_sum = yearly_cat.pivot(index="year", columns="category", values="再生数合計").fillna(0)
    for c in ["ボイロ系", "ボカロ系"]:
        if c not in pivot_views_sum.columns:
            pivot_views_sum[c] = 0
    pivot_views_sum = pivot_views_sum[["ボイロ系", "ボカロ系"]]
    pivot_views_sum.plot(kind="bar", stacked=True, ax=axes[0, 0], color=[colors["ボイロ系"], colors["ボカロ系"]], width=0.55, rot=0)
    axes[0, 0].set_title("年別 総再生数（ボカロ vs ボイロ）", fontsize=12, fontweight="bold")
    axes[0, 0].set_xlabel("年", fontsize=10)
    axes[0, 0].set_ylabel("総再生数 (回)", fontsize=10)
    axes[0, 0].yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x):,}"))
    axes[0, 0].grid(axis="y", linestyle="--", alpha=0.7)
    axes[0, 0].legend(title="カテゴリ")

    for cat in ["ボイロ系", "ボカロ系"]:
        sub_cat = yearly_cat[yearly_cat["category"] == cat]
        if len(sub_cat) > 0:
            axes[0, 1].plot(sub_cat["year"], sub_cat["再生数中央値"], marker="o", linewidth=2.5, label=cat, color=colors[cat])
    axes[0, 1].set_xticks(all_years)
    axes[0, 1].set_title("年別 再生数中央値（ボカロ vs ボイロ）", fontsize=12, fontweight="bold")
    axes[0, 1].set_xlabel("年", fontsize=10)
    axes[0, 1].set_ylabel("再生数中央値 (回)", fontsize=10)
    axes[0, 1].grid(True, linestyle="--", alpha=0.7)
    axes[0, 1].legend(title="カテゴリ")

    pivot_likes_sum = yearly_cat.pivot(index="year", columns="category", values="いいね合計").fillna(0)
    for c in ["ボイロ系", "ボカロ系"]:
        if c not in pivot_likes_sum.columns:
            pivot_likes_sum[c] = 0
    pivot_likes_sum = pivot_likes_sum[["ボイロ系", "ボカロ系"]]
    pivot_likes_sum.plot(kind="bar", stacked=True, ax=axes[1, 0], color=[colors["ボイロ系"], colors["ボカロ系"]], width=0.55, rot=0)
    axes[1, 0].set_title("年別 総いいね数（ボカロ vs ボイロ）", fontsize=12, fontweight="bold")
    axes[1, 0].set_xlabel("年", fontsize=10)
    axes[1, 0].set_ylabel("総いいね数 (回)", fontsize=10)
    axes[1, 0].yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x):,}"))
    axes[1, 0].grid(axis="y", linestyle="--", alpha=0.7)
    axes[1, 0].legend(title="カテゴリ")

    for cat in ["ボイロ系", "ボカロ系"]:
        sub_cat = yearly_cat[yearly_cat["category"] == cat]
        if len(sub_cat) > 0:
            axes[1, 1].plot(sub_cat["year"], sub_cat["いいね中央値"], marker="s", linewidth=2.5, label=cat, color=colors[cat])
    axes[1, 1].set_xticks(all_years)
    axes[1, 1].set_title("年別 いいね数中央値（ボカロ vs ボイロ）", fontsize=12, fontweight="bold")
    axes[1, 1].set_xlabel("年", fontsize=10)
    axes[1, 1].set_ylabel("いいね数中央値 (回)", fontsize=10)
    axes[1, 1].grid(True, linestyle="--", alpha=0.7)
    axes[1, 1].legend(title="カテゴリ")

    plt.tight_layout()
    p2 = OUTPUT_DIR / "02_ririse_views_and_likes.png"
    plt.savefig(p2, dpi=300)
    plt.close()
    print(f"Saved: {p2}")

    # -------------------------------------------------------------
    # Chart 3: ジャンル別投稿数の年次推移（ラジオ、ASMR追加）
    # -------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(17, 6))

    genre_cols = [g for g in GENRE_ORDER if g in genre_df.columns]
    plot_genre_df = genre_df.set_index("年")[genre_cols]

    # 積み上げ棒グラフ
    c_list = [colors.get(c, "#777") for c in genre_cols]
    plot_genre_df.plot(kind="bar", stacked=True, ax=axes[0], color=c_list, width=0.6, edgecolor="white", rot=0)
    axes[0].set_title("ジャンル別 投稿数推移（彩澄りりせ）", fontsize=13, fontweight="bold", pad=12)
    axes[0].set_xlabel("年", fontsize=11)
    axes[0].set_ylabel("投稿数 (本)", fontsize=11)
    axes[0].grid(axis="y", linestyle="--", alpha=0.7)
    axes[0].legend(title="ジャンル", bbox_to_anchor=(1.02, 1), loc="upper left")

    # 100%積み上げ棒グラフ（比率推移）
    genre_pct_df = plot_genre_df.div(plot_genre_df.sum(axis=1), axis=0) * 100
    genre_pct_df.plot(kind="bar", stacked=True, ax=axes[1], color=c_list, width=0.6, edgecolor="white", rot=0)
    axes[1].set_title("ジャンル別 構成比率推移（%）", fontsize=13, fontweight="bold", pad=12)
    axes[1].set_xlabel("年", fontsize=11)
    axes[1].set_ylabel("シェア (%)", fontsize=11)
    axes[1].set_ylim(0, 100)
    axes[1].grid(axis="y", linestyle="--", alpha=0.7)
    axes[1].legend(title="ジャンル", bbox_to_anchor=(1.02, 1), loc="upper left")

    plt.tight_layout()
    p3 = OUTPUT_DIR / "03_ririse_genre_breakdown.png"
    plt.savefig(p3, dpi=300)
    plt.close()
    print(f"Saved: {p3}")

    # -------------------------------------------------------------
    # Chart 4: ショート・ロング比率（2026/4/15以降）
    # -------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    labels = [f"ロング ({short_summary['long_ratio']:.1f}%)", f"ショート ({short_summary['short_ratio']:.1f}%)"]
    counts = [short_summary["long_count"], short_summary["short_count"]]
    chart_colors = [colors["long"], colors["short"]]
    wedges, texts, autotexts = axes[0].pie(
        counts,
        labels=labels,
        autopct="%1.1f%%",
        pctdistance=0.75,
        startangle=90,
        colors=chart_colors,
        textprops=dict(color="#333", fontsize=11, fontweight="bold"),
        wedgeprops=dict(width=0.45, edgecolor="white", linewidth=2),
    )
    for autotext in autotexts:
        autotext.set_color("white")
        autotext.set_weight("bold")
        autotext.set_fontsize(11)
    axes[0].set_title(f"2026/4/15以降の動画種別比率 (計{short_summary['total_recent']}本)", fontsize=13, fontweight="bold", pad=12)

    recent_df = short_summary["recent_df"]
    cat_type_df = recent_df.groupby(["category", "contentType"]).size().unstack(fill_value=0)
    cat_type_df = cat_type_df[["long", "short"]]
    cat_type_df.plot(kind="bar", stacked=True, ax=axes[1], color=[colors["long"], colors["short"]], width=0.45, edgecolor="white", rot=0)
    axes[1].set_title("カテゴリ別 ショート / ロング 内訳 (2026/4/15以降)", fontsize=13, fontweight="bold", pad=12)
    axes[1].set_xlabel("カテゴリ", fontsize=11)
    axes[1].set_ylabel("投稿本数 (本)", fontsize=11)
    axes[1].grid(axis="y", linestyle="--", alpha=0.7)
    axes[1].legend(["ロング (long)", "ショート (short)"], title="動画種別", bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=9)
    for c in axes[1].containers:
        for p in c:
            val = int(p.get_height())
            if val > 0:
                axes[1].annotate(f"{val}", (p.get_x() + p.get_width() / 2, p.get_y() + val / 2),
                                ha="center", va="center", color="white", fontweight="bold", fontsize=10)

    plt.tight_layout()
    p4 = OUTPUT_DIR / "04_ririse_short_vs_long.png"
    plt.savefig(p4, dpi=300)
    plt.close()
    print(f"Saved: {p4}")

    # -------------------------------------------------------------
    # Chart 0: サマリーダッシュボード (4枚統合)
    # -------------------------------------------------------------
    fig = plt.figure(figsize=(18, 12))
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.25)

    ax1 = fig.add_subplot(gs[0, 0])
    posts_with_proj.plot(kind="bar", stacked=True, ax=ax1, color=[colors["ボイロ系"], colors["ボカロ系"]], width=0.55, edgecolor="white", rot=0)
    ax1.set_title("(1) 年別 投稿数推移 & 2026年着地予測", fontsize=12, fontweight="bold")
    ax1.set_xlabel("年", fontsize=10)
    ax1.set_ylabel("投稿本数 (本)", fontsize=10)
    ax1.grid(axis="y", linestyle="--", alpha=0.7)
    ax1.legend(title="カテゴリ")

    ax2 = fig.add_subplot(gs[0, 1])
    for cat in ["ボイロ系", "ボカロ系"]:
        sub_cat = yearly_cat[yearly_cat["category"] == cat]
        if len(sub_cat) > 0:
            ax2.plot(sub_cat["year"], sub_cat["再生数中央値"], marker="o", linewidth=2.2, label=f"{cat} (再生中央値)", color=colors[cat])
    ax2.set_xticks(all_years)
    ax2.set_title("(2) 年別 再生数中央値推移", fontsize=12, fontweight="bold")
    ax2.set_xlabel("年", fontsize=10)
    ax2.set_ylabel("再生数中央値 (回)", fontsize=10)
    ax2.grid(True, linestyle="--", alpha=0.7)
    ax2.legend()

    ax3 = fig.add_subplot(gs[1, 0])
    genre_pct_df.plot(kind="bar", stacked=True, ax=ax3, color=c_list, width=0.6, edgecolor="white", rot=0)
    ax3.set_title("(3) ジャンル別 構成比率推移（%）", fontsize=12, fontweight="bold")
    ax3.set_xlabel("年", fontsize=10)
    ax3.set_ylabel("シェア (%)", fontsize=10)
    ax3.set_ylim(0, 100)
    ax3.grid(axis="y", linestyle="--", alpha=0.7)
    ax3.legend(title="ジャンル", bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=9)

    ax4 = fig.add_subplot(gs[1, 1])
    cat_type_df.plot(kind="bar", stacked=True, ax=ax4, color=[colors["long"], colors["short"]], width=0.45, edgecolor="white", rot=0)
    ax4.set_title("(4) 2026/4/15以降 ショート/ロング内訳", fontsize=12, fontweight="bold")
    ax4.set_xlabel("カテゴリ", fontsize=10)
    ax4.set_ylabel("投稿本数 (本)", fontsize=10)
    ax4.grid(axis="y", linestyle="--", alpha=0.7)
    ax4.legend(["ロング (long)", "ショート (short)"], title="動画種別", bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=9)
    for c in ax4.containers:
        for p in c:
            val = int(p.get_height())
            if val > 0:
                ax4.annotate(f"{val}", (p.get_x() + p.get_width() / 2, p.get_y() + val / 2),
                            ha="center", va="center", color="white", fontweight="bold", fontsize=10)

    fig.suptitle("タグ「彩澄りりせ」 ニコニコ動画総合分析ダッシュボード", fontsize=16, fontweight="bold", y=0.98)
    p0 = OUTPUT_DIR / "00_ririse_dashboard.png"
    plt.savefig(p0, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {p0}")


def format_dataframe(df_in: pd.DataFrame) -> pd.DataFrame:
    """Markdown表示用に数値を通貨カンマ形式や小数点フォーマットに整える"""
    df_out = df_in.copy()
    for col in df_out.columns:
        if "数" in col or "件" in col or "人" in col or "本" in col or "合計" in col or "実績" in col or "予測" in col:
            if pd.api.types.is_numeric_dtype(df_out[col]):
                df_out[col] = df_out[col].apply(lambda x: f"{int(x):,}" if pd.notnull(x) else "-")
        elif "平均" in col or "秒" in col or "ratio" in col.lower() or "率" in col:
            if pd.api.types.is_numeric_dtype(df_out[col]):
                df_out[col] = df_out[col].apply(lambda x: f"{x:,.1f}" if pd.notnull(x) else "-")
        elif "中央値" in col:
            if pd.api.types.is_numeric_dtype(df_out[col]):
                df_out[col] = df_out[col].apply(lambda x: f"{x:,.1f}" if (x % 1 != 0) else f"{int(x):,}")
    return df_out


def generate_markdown_report(yearly_all: pd.DataFrame, yearly_cat: pd.DataFrame, genre_df: pd.DataFrame, short_summary: dict, proj_summary: dict) -> str:
    """Markdownレポートの生成"""
    md = []
    md.append("# タグ「彩澄りりせ」ニコニコ動画データ解析レポート\n")
    md.append(f"- **データ取得元**: ニコニコ動画 スナップショット検索API v2 (`tagsExact`: 彩澄りりせ)")
    md.append(f"- **表示対象制限**:")
    md.append(f"  - **ボイロ系**: 2022年以降（VOICEPEAK 彩澄りりせ発売以降）")
    md.append(f"  - **ボカロ系**: 2025年以降（Synthesizer V 2 AI 彩澄りりせ発売以降）")
    md.append(f"- **解析対象動画件数**: {yearly_all['投稿数'].sum():,} 件\n")

    md.append("## 1. 各年ごとの統計（投稿数、投稿者数、再生数、いいね数）\n")
    md.append("### ■ 全体集計")
    md.append(format_dataframe(yearly_all).to_markdown(index=False))
    
    md.append("\n### ■ ボカロ系 vs ボイロ系 分割集計")
    md.append("> **ボカロ判定基準**: タグに `VOCALOID|VOCAROID|音楽|歌うボイスロイド|カバー曲|歌ってみた|SynthesizerV` を含む動画\n")
    md.append(format_dataframe(yearly_cat).to_markdown(index=False))
    
    md.append("\n![年別投稿数・投稿者数推移](01_ririse_posts_and_users.png)")
    md.append("![年別再生数・いいね数推移](02_ririse_views_and_likes.png)\n")

    md.append("## 2. 2026年 年間投稿数 着地予測（年間換算）\n")
    md.append(f"- **現在時点（データ基準日）**: 2026年8月15日（経過日数: 約{proj_summary['elapsed_days']:.1f}日 / 年間進捗率: {proj_summary['progress_rate']:.1f}%）")
    md.append(f"- **年間換算係数**: `{proj_summary['annual_factor']:.4f}`倍\n")
    md.append(format_dataframe(proj_summary["proj_df"]).to_markdown(index=False))
    md.append(f"\n> **予測ハイライト**:")
    total_yoy_str = f"{proj_summary['total_yoy']:+.1f}%" if proj_summary['total_yoy'] is not None else "算出不可"
    voiro_yoy_str = f"{proj_summary['voiro_yoy']:+.1f}%" if proj_summary['voiro_yoy'] is not None else "算出不可"
    vocalo_yoy_str = f"{proj_summary['vocalo_yoy']:+.1f}%" if proj_summary['vocalo_yoy'] is not None else "算出不可"

    md.append(f"> - **全体投稿数**: 2025年実績 956本 → **2026年着地予測 {proj_summary['total_proj']:,}本**（前年比 **{total_yoy_str}**）")
    md.append(f"> - **ボイロ系**: 2025年実績 768本 → **2026年着地予測 {proj_summary['voiro_proj']:,}本**（前年比 **{voiro_yoy_str}**）")
    md.append(f"> - **ボカロ系**: 2025年実績 188本 → **2026年着地予測 {proj_summary['vocalo_proj']:,}本**（前年比 **{vocalo_yoy_str}** と倍増ペース）\n")

    md.append("## 3. ジャンル別 投稿数推移\n")
    md.append("> **ジャンル定義**:")
    md.append("> - **ボカロ**: タグに `VOCALOID|VOCAROID|音楽|歌うボイスロイド|カバー曲|歌ってみた|SynthesizerV` を含む（2025年以降）")
    md.append("> - **実況**: 非ボカロ かつ タグに「実況」を含む")
    md.append("> - **解説**: 非ボカロ かつ タグに「解説」を含む")
    md.append("> - **劇場**: 非ボカロ かつ タグに「劇場」を含む")
    md.append("> - **ラジオ**: 非ボカロ かつ タグに「ラジオ」または「雑談」を含む")
    md.append("> - **ASMR**: 非ボカロ かつ タグに「ASMR」「ASMROID」「バイノーラル」「耳かき」を含む")
    md.append("> - **車載**: 非ボカロ かつ タグに「車載」を含む")
    md.append("> - **旅行**: 非ボカロ かつ タグに「旅行」「岐阜県」「広島県」「山口県」「観光スポット」「神社巡り」「寺巡り」「日本の風景」を含む")
    md.append("> - **キッチン**: 非ボカロ かつ タグに「キッチン」を含む")
    md.append("> - **その他ボイロ**: 上記のいずれにも該当しない非ボカロ動画\n")
    md.append(format_dataframe(genre_df).to_markdown(index=False))
    md.append("\n![ジャンル別推移](03_ririse_genre_breakdown.png)\n")

    md.append("## 4. ショート・ロング比率（2026/4/15以降）\n")
    md.append(f"- **対象期間**: 2026年4月15日（ショート動画機能公開）以降")
    md.append(f"- **総投稿数**: {short_summary['total_recent']:,} 本")
    md.append(f"- **ロング動画 (`long`)**: {short_summary['long_count']:,} 本 ({short_summary['long_ratio']:.1f}%)")
    md.append(f"- **ショート動画 (`short`)**: {short_summary['short_count']:,} 本 ({short_summary['short_ratio']:.1f}%)\n")
    
    md.append("### ■ 2026/4/15以降のカテゴリ・種別別詳細")
    md.append(format_dataframe(short_summary["breakdown"]).to_markdown(index=False))
    md.append("\n![ショート・ロング比率](04_ririse_short_vs_long.png)\n")

    report_content = "\n".join(md)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report_content)
    print(f"Saved markdown report to {REPORT_PATH}")
    return report_content


def main():
    df = load_and_preprocess_data()
    yearly_all, yearly_cat = analyze_yearly_stats(df)
    genre_df = analyze_genre_stats(df)
    short_summary = analyze_short_ratio(df)
    proj_summary = calculate_2026_projection(df)

    plot_visualizations(df, yearly_all, yearly_cat, genre_df, short_summary, proj_summary)
    report = generate_markdown_report(yearly_all, yearly_cat, genre_df, short_summary, proj_summary)
    print("\n" + "=" * 80)
    print(" 解析・可視化完了！")
    print("=" * 80)


if __name__ == "__main__":
    main()
