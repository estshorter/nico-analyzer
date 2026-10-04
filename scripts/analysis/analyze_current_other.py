import pickle
import pandas as pd
from collections import Counter

with open("results/ririse.pickle", "rb") as f:
    recv = pickle.load(f)
df = pd.json_normalize(recv["data"])
df["startTime"] = pd.to_datetime(df["startTime"])
df["year"] = df["startTime"].dt.year
VOCALO_PATTERN = r"VOCALOID|VOCAROID|音楽|歌うボイスロイド|カバー曲|歌ってみた|SynthesizerV"
df["is_vocalo"] = df["tags"].fillna("").str.contains(VOCALO_PATTERN, case=False, regex=True)

df_filtered = df[((~df["is_vocalo"]) & (df["year"] >= 2022)) | ((df["is_vocalo"]) & (df["year"] >= 2025))].copy()

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
combined_pat = "|".join(GENRE_PATTERNS.values())

voiro_df = df_filtered[~df_filtered["is_vocalo"]].copy()
has_any = voiro_df["tags"].str.contains(combined_pat, case=False, regex=True)
other_df = voiro_df[~has_any].copy()

out = []
out.append(f"=== 現在の「その他ボイロ」動画 全{len(other_df)}件の分析 ===\n")
out.append("■ 年別件数:")
for y, cnt in other_df["year"].value_counts().sort_index().items():
    out.append(f"  - {y}年: {cnt}本")

out.append("\n■ 全期間での頻出タグ Top 30:")
all_tags = []
for t_str in other_df["tags"]:
    tags = [t.strip() for t in t_str.split(" ") if t.strip()]
    all_tags.extend(tags)
c = Counter(all_tags)
for tag, cnt in c.most_common(35):
    if tag in ["彩澄りりせ"]:
        continue
    out.append(f"  - {tag}: {cnt}本 ({cnt/len(other_df)*100:.1f}%)")

out.append("\n■ 代表的な動画タイトル（再生数上位 25件）:")
for i, (_, r) in enumerate(other_df.sort_values("viewCounter", ascending=False).head(25).iterrows(), 1):
    out.append(f"{i}. [{r['year']}年 / {r['viewCounter']}再生 / {r['likeCounter']}いいね] {r['title']}")
    out.append(f"   URL: https://www.nicovideo.jp/watch/{r['contentId']}")
    out.append(f"   タグ: {r['tags']}")

# 年別（特に2024, 2025, 2026）の主なカテゴリ分類
out.append("\n■ サブカテゴリ分類（推計）:")
# 朗読・文学
roudoku = other_df["tags"].str.contains(r"朗読|青空文庫|本", case=False)
# 投稿祭・企画
toukousai = other_df["tags"].str.contains(r"祭|企画|イベント", case=False)
# ゲーム系（実況タグなし）
game = other_df["tags"].str.contains(r"steam|ゲーム|play|game|アーマードコア|undying", case=False)
# 立ち絵・素材・紹介
material = other_df["tags"].str.contains(r"立ち絵|素材|自己紹介|ソフトウェアトーク|voicepeak", case=False)
# 科学・事故・アカデミック
science = other_df["tags"].str.contains(r"科学|事故|メーデー|考察|認知科学", case=False)
# 模型・工作・釣り
hobby = other_df["tags"].str.contains(r"模型|Nゲージ|釣り|フィッシング|登山", case=False)

out.append(f"  1. 投稿祭・コラボ・企画系: {toukousai.sum()}本 ({toukousai.sum()/len(other_df)*100:.1f}%)")
out.append(f"  2. ゲームプレイ動画（実況タグなし）: {game.sum()}本 ({game.sum()/len(other_df)*100:.1f}%)")
out.append(f"  3. 朗読・文学・小説系: {roudoku.sum()}本 ({roudoku.sum()/len(other_df)*100:.1f}%)")
out.append(f"  4. 科学・事故・考察・アカデミック系: {science.sum()}本 ({science.sum()/len(other_df)*100:.1f}%)")
out.append(f"  5. 趣味・模型・釣り・工作・登山系: {hobby.sum()}本 ({hobby.sum()/len(other_df)*100:.1f}%)")
out.append(f"  6. 立ち絵配布・自己紹介・キャラ紹介系: {material.sum()}本 ({material.sum()/len(other_df)*100:.1f}%)")

with open("results/current_other_analysis.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("Saved to results/current_other_analysis.txt")
