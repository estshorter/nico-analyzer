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

GENRES = ["実況", "解説", "劇場", "キッチン", "車載", "旅行"]
voiro_df = df_filtered[~df_filtered["is_vocalo"]].copy()
has_any = voiro_df["tags"].str.contains("|".join(GENRES), case=False)
voiro_other = voiro_df[~has_any].copy()

other_2025 = voiro_other[voiro_other["year"] == 2025]

radio_mask = other_2025["tags"].str.contains("ラジオ|雑談", case=False)
place_mask = other_2025["tags"].str.contains("岐阜県|山口県|広島県|観光|神社|風景|寺|周防大島", case=False)
read_mask = other_2025["tags"].str.contains("朗読|青空文庫|本", case=False)
fes_mask = other_2025["tags"].str.contains("祭", case=False)
science_mask = other_2025["tags"].str.contains("科学|事故|メーデー|考察", case=False)
game_mask = other_2025["tags"].str.contains("steam|ゲーム|play|game", case=False)

out = []
out.append(f"2025年 その他ボイロ全体: {len(other_2025)}本")
out.append(f"  - ラジオ・雑談系: {radio_mask.sum()}本 ({radio_mask.sum()/len(other_2025)*100:.1f}%)")
out.append(f"  - ご当地・スポット・名所紹介系: {place_mask.sum()}本 ({place_mask.sum()/len(other_2025)*100:.1f}%)")
out.append(f"  - 朗読・文学系: {read_mask.sum()}本 ({read_mask.sum()/len(other_2025)*100:.1f}%)")
out.append(f"  - 投稿祭・イベント系: {fes_mask.sum()}本 ({fes_mask.sum()/len(other_2025)*100:.1f}%)")
out.append(f"  - 事故・科学・知識系: {science_mask.sum()}本 ({science_mask.sum()/len(other_2025)*100:.1f}%)")
out.append(f"  - ゲームプレイ系(実況タグなし): {game_mask.sum()}本 ({game_mask.sum()/len(other_2025)*100:.1f}%)")

out.append("\n--- 2025年 その他ボイロの再生数上位動画 ---")
top_vids = other_2025.sort_values("viewCounter", ascending=False).head(15)
for _, r in top_vids.iterrows():
    out.append(f"・[{r['viewCounter']}再生 / {r['likeCounter']}いいね] {r['title']}")
    out.append(f"    タグ: {r['tags']}")

with open("results/other_2025_breakdown.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("Saved to results/other_2025_breakdown.txt")
