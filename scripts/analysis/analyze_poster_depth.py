import pickle
import datetime
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib_fontja
import seaborn as sns
from common_utils import filter_software_talk

# グラフ描画スタイルの設定
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = ["IPAexGothic", "Hiragino Sans", "Yu Gothic", "Meiryo", "sans-serif"]

def analyze_and_plot():
    pickle_path = Path("results/software_talk.pickle")
    print(f"Loading dataset: {pickle_path}...")
    with open(pickle_path, "rb") as f:
        recv = pickle.load(f)
    
    df = pd.json_normalize(recv["data"])
    print(f"Raw data count: {len(df)}")
    
    # 【必須ルール】filter_software_talk の適用
    df = filter_software_talk(df)
    
    df["startTime"] = pd.to_datetime(df["startTime"])
    df = df.sort_values("startTime", ignore_index=True)
    
    # userId == 0 の除外
    df.fillna({"userId": 0}, inplace=True)
    df["userId"] = df["userId"].astype("uint64")
    df = df[df["userId"] != 0].copy()
    
    # 2025年までに制限
    df = df[df["startTime"].dt.year <= 2025].copy()
    print(f"Target data count (userId != 0 & year <= 2025): {len(df)}")
    
    # 全体での直前投稿日時とボイロ全体初投稿日時の計算
    df["overall_prev_startTime"] = df.groupby("userId")["startTime"].shift(1)
    df["overall_first_startTime"] = df.groupby("userId")["startTime"].transform("min")
    df["overall_first_year"] = df["overall_first_startTime"].dt.year
    df["year"] = df["startTime"].dt.year

    # 年y・ユーザーごとの「ボイロ全体での年内最初の投稿行」を抽出
    first_overall_posts_by_year = df.groupby(["year", "userId"]).first().reset_index()

    genres = {
        "overall": ("ボイロ全体", None),
        "game": ("ボイロ実況", "実況プレイ"),
        "theater": ("ボイロ劇場", "劇場"),
        "explanation": ("ボイロ解説", "解説"),
        "kitchen": ("ボイロキッチン", "キッチン"),
        "car": ("ボイロ車載", "車載"),
        "travel": ("ボイロ旅行", "旅行"),
    }
    
    summary_rows = []
    
    output_dir = Path("results/poster_depth")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for g_key, (g_title, tag_kw) in genres.items():
        print(f"\nProcessing [{g_title}] ...")
        if tag_kw is None:
            df_g = df.copy()
        else:
            df_g = df[df["tags"].astype(str).str.contains(tag_kw, case=False, na=False)].copy()
            
        df_g = df_g.sort_values("startTime", ignore_index=True)
        
        # ジャンル内での前回の投稿日時・ジャンル内初投稿日時
        df_g["genre_prev_startTime"] = df_g.groupby("userId")["startTime"].shift(1)
        df_g["genre_first_startTime"] = df_g.groupby("userId")["startTime"].transform("min")
        df_g["genre_first_year"] = df_g["genre_first_startTime"].dt.year
        
        df_g["year"] = df_g["startTime"].dt.year
        
        # 各年・ユーザーごとのX年中最初の投稿行を取り出す
        first_posts_in_year = df_g.groupby(["year", "userId"]).first().reset_index()
        
        years = list(range(2011, 2026))
        
        for y in years:
            posts_y = first_posts_in_year[first_posts_in_year["year"] == y]
            total_posters = len(posts_y)
            
            if total_posters == 0:
                continue
                
            # --- 軸A: ボイロ全体軸 ---
            # 年yにおける、該当ユーザーのボイロ全体での最初の投稿行を取得
            overall_posts_y = first_overall_posts_by_year[first_overall_posts_by_year["year"] == y]
            merged_overall = pd.merge(posts_y[["userId"]], overall_posts_y, on="userId", how="inner")
            
            new_overall = (merged_overall["overall_first_year"] == y).sum()
            existing_overall = merged_overall[merged_overall["overall_first_year"] < y]
            blank_overall = (existing_overall["startTime"] - existing_overall["overall_prev_startTime"]).dt.total_seconds() / 86400.0
            cont_overall = (blank_overall <= 365).sum()
            ret_overall = (blank_overall > 365).sum()
            
            # --- 軸B: ジャンル内軸 ---
            new_genre = (posts_y["genre_first_year"] == y).sum()
            existing_genre = posts_y[posts_y["genre_first_year"] < y]
            blank_genre = (existing_genre["startTime"] - existing_genre["genre_prev_startTime"]).dt.total_seconds() / 86400.0
            cont_genre = (blank_genre <= 365).sum()
            ret_genre = (blank_genre > 365).sum()
            
            summary_rows.append({
                "genre_key": g_key,
                "genre_name": g_title,
                "year": y,
                "total_posters": total_posters,
                
                # 軸A: ボイロ全体軸
                "overall_new": new_overall,
                "overall_continued": cont_overall,
                "overall_returned": ret_overall,
                
                # 軸B: ジャンル内軸
                "genre_new": new_genre,
                "genre_continued": cont_genre,
                "genre_returned": ret_genre,
                
                # 派生指標: 他ジャンルからの新規流入者（ジャンル新規だがボイロ全体新規ではない）
                "genre_inflow_from_other": new_genre - new_overall,
                
                # 比率指標 (%)
                "overall_new_ratio": (new_overall / total_posters) * 100,
                "genre_new_ratio": (new_genre / total_posters) * 100,
                "genre_inflow_ratio": ((new_genre - new_overall) / total_posters) * 100,
            })
            
    res_df = pd.DataFrame(summary_rows)
    
    # CSV出力
    csv_path = output_dir / "poster_depth_summary.csv"
    res_df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"\nSaved CSV: {csv_path}")

    # -------------------------------------------------------------
    # グラフ描画処理
    # -------------------------------------------------------------
    for g_key, (g_title, _) in genres.items():
        g_data = res_df[res_df["genre_key"] == g_key].copy()
        if len(g_data) == 0:
            continue
            
        fig, axes = plt.subplots(1, 2, figsize=(16, 6), sharey=True)
        x = g_data["year"]
        
        # 1. 軸A: ボイロ全体初投稿 基準
        ax1 = axes[0]
        p1_cont = ax1.bar(x, g_data["overall_continued"], label="継続投稿者 (ブランク1年未満)", color="#2b5c8f", alpha=0.85)
        p1_ret = ax1.bar(x, g_data["overall_returned"], bottom=g_data["overall_continued"], label="復帰投稿者 (ブランク1年以上)", color="#6baed6", alpha=0.85)
        p1_new = ax1.bar(x, g_data["overall_new"], bottom=g_data["overall_continued"] + g_data["overall_returned"], label="新規投稿者 (ボイロ全体初投稿)", color="#e6550d", alpha=0.9)
        
        ax1.set_title(f"{g_title} - 【軸A】ボイロ全体初投稿 基準", fontsize=13, fontweight="bold")
        ax1.set_xlabel("年")
        ax1.set_ylabel("投稿者数")
        ax1.legend(loc="upper left")
        ax1.grid(True, linestyle=":", alpha=0.6)
        
        # 2. 軸B: ジャンル内初投稿 基準
        ax2 = axes[1]
        p2_cont = ax2.bar(x, g_data["genre_continued"], label="継続投稿者 (ブランク1年未満)", color="#2b5c8f", alpha=0.85)
        p2_ret = ax2.bar(x, g_data["genre_returned"], bottom=g_data["genre_continued"], label="復帰投稿者 (ブランク1年以上)", color="#6baed6", alpha=0.85)
        p2_new = ax2.bar(x, g_data["genre_new"], bottom=g_data["genre_continued"] + g_data["genre_returned"], label="新規投稿者 (ジャンル内初投稿)", color="#d94701", alpha=0.9)
        
        ax2.set_title(f"{g_title} - 【軸B】ジャンル内初投稿 基準", fontsize=13, fontweight="bold")
        ax2.set_xlabel("年")
        ax2.legend(loc="upper left")
        ax2.grid(True, linestyle=":", alpha=0.6)
        
        plt.suptitle(f"{g_title} 投稿者構造の推移（積み上げ棒グラフ）", fontsize=15, fontweight="bold", y=1.02)
        plt.tight_layout()
        
        plot_path = output_dir / f"{g_key}_poster_breakdown_comparison.png"
        plt.savefig(plot_path, dpi=300, bbox_inches="tight")
        plt.close("all")
        print(f"Saved plot: {plot_path}")

        # --- 新規追加: 折れ線グラフによる各区分単体の推移比較 ---
        fig, axes = plt.subplots(1, 2, figsize=(16, 6), sharey=True)
        
        # 1. 軸A: ボイロ全体初投稿 基準 (折れ線)
        ax1 = axes[0]
        ax1.plot(x, g_data["overall_continued"], marker="o", label="継続投稿者 (ブランク1年未満)", color="#2b5c8f", linewidth=2.5)
        ax1.plot(x, g_data["overall_new"], marker="s", label="新規投稿者 (ボイロ全体初投稿)", color="#e6550d", linewidth=2.5)
        ax1.plot(x, g_data["overall_returned"], marker="^", label="復帰投稿者 (ブランク1年以上)", color="#6baed6", linewidth=2.5, linestyle="--")
        
        ax1.set_title(f"{g_title} - 【軸A】各区分推移 (ボイロ全体基準)", fontsize=13, fontweight="bold")
        ax1.set_xlabel("年")
        ax1.set_ylabel("人数")
        ax1.legend(loc="upper left")
        ax1.grid(True, linestyle=":", alpha=0.6)
        
        # 2. 軸B: ジャンル内初投稿 基準 (折れ線)
        ax2 = axes[1]
        ax2.plot(x, g_data["genre_continued"], marker="o", label="継続投稿者 (ブランク1年未満)", color="#2b5c8f", linewidth=2.5)
        ax2.plot(x, g_data["genre_new"], marker="s", label="新規投稿者 (ジャンル内初投稿)", color="#d94701", linewidth=2.5)
        ax2.plot(x, g_data["genre_returned"], marker="^", label="復帰投稿者 (ブランク1年以上)", color="#6baed6", linewidth=2.5, linestyle="--")
        
        ax2.set_title(f"{g_title} - 【軸B】各区分推移 (ジャンル内基準)", fontsize=13, fontweight="bold")
        ax2.set_xlabel("年")
        ax2.legend(loc="upper left")
        ax2.grid(True, linestyle=":", alpha=0.6)
        
        plt.suptitle(f"{g_title} 区分別投稿者数推移（折れ線グラフ）", fontsize=15, fontweight="bold", y=1.02)
        plt.tight_layout()
        
        line_plot_path = output_dir / f"{g_key}_poster_breakdown_lines.png"
        plt.savefig(line_plot_path, dpi=300, bbox_inches="tight")
        plt.close("all")
        print(f"Saved line plot: {line_plot_path}")

    # 3. 流入分析グラフ (他ジャンルからの流入 vs 完全新規)
    fig, ax = plt.subplots(figsize=(12, 6))
    for g_key, (g_title, _) in genres.items():
        if g_key == "overall":
            continue
        g_data = res_df[res_df["genre_key"] == g_key]
        ax.plot(g_data["year"], g_data["genre_inflow_from_other"], marker="o", label=f"{g_title} (他ジャンルからの参入)")
        
    ax.set_title("ジャンル別・他ジャンルからの流入新規投稿者数推移 (ボイロ既投稿者の新ジャンル挑戦)", fontsize=14, fontweight="bold")
    ax.set_xlabel("年")
    ax.set_ylabel("流入人数 (ジャンル新規 - ボイロ全体新規)")
    ax.legend(loc="upper left")
    ax.grid(True, linestyle=":", alpha=0.6)
    
    inflow_plot_path = output_dir / "genre_inflow_comparison.png"
    plt.savefig(inflow_plot_path, dpi=300, bbox_inches="tight")
    plt.close("all")
    print(f"Saved inflow plot: {inflow_plot_path}")

    # 4. 新規投稿者比率のジャンル間比較グラフ
    fig, axes = plt.subplots(1, 2, figsize=(16, 6), sharey=True)
    
    # 4a. 完全新規率 (%) の比較
    ax1 = axes[0]
    for g_key, (g_title, _) in genres.items():
        g_data = res_df[res_df["genre_key"] == g_key]
        linestyle = "--" if g_key == "overall" else "-"
        linewidth = 3 if g_key == "overall" else 2
        ax1.plot(g_data["year"], g_data["overall_new_ratio"], marker="o", label=f"{g_title}", linestyle=linestyle, linewidth=linewidth)
        
    ax1.set_title("【完全新規率 (%)】ボイロ全体初投稿者の割合", fontsize=13, fontweight="bold")
    ax1.set_xlabel("年")
    ax1.set_ylabel("比率 (%)")
    ax1.set_ylim(0, 100)
    ax1.legend(loc="upper right")
    ax1.grid(True, linestyle=":", alpha=0.6)
    
    # 4b. ジャンル内新規率 (%) の比較
    ax2 = axes[1]
    for g_key, (g_title, _) in genres.items():
        g_data = res_df[res_df["genre_key"] == g_key]
        linestyle = "--" if g_key == "overall" else "-"
        linewidth = 3 if g_key == "overall" else 2
        ax2.plot(g_data["year"], g_data["genre_new_ratio"], marker="o", label=f"{g_title}", linestyle=linestyle, linewidth=linewidth)
        
    ax2.set_title("【ジャンル内新規率 (%)】ジャンル内初投稿者の割合", fontsize=13, fontweight="bold")
    ax2.set_xlabel("年")
    ax2.set_ylim(0, 100)
    ax2.legend(loc="upper right")
    ax2.grid(True, linestyle=":", alpha=0.6)
    
    plt.suptitle("ジャンル別・新規投稿者比率の比較（完全新規率 vs ジャンル内新規率）", fontsize=15, fontweight="bold", y=1.02)
    plt.tight_layout()
    
    ratio_plot_path = output_dir / "genre_new_ratio_comparison.png"
    plt.savefig(ratio_plot_path, dpi=300, bbox_inches="tight")
    plt.close("all")
    print(f"Saved ratio plot: {ratio_plot_path}")

    print("\nProcessing finished successfully!")

if __name__ == "__main__":
    analyze_and_plot()
