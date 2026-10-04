import pickle
import pandas as pd

with open("results/ririse.pickle", "rb") as f:
    recv = pickle.load(f)
df = pd.json_normalize(recv["data"])
df["startTime"] = pd.to_datetime(df["startTime"])
df["year"] = df["startTime"].dt.year
VOCALO_PATTERN = r"VOCALOID|VOCAROID|音楽|歌うボイスロイド|カバー曲|歌ってみた|SynthesizerV"
df["is_vocalo"] = df["tags"].fillna("").str.contains(VOCALO_PATTERN, case=False, regex=True)

df_filtered = df[((~df["is_vocalo"]) & (df["year"] >= 2022)) | ((df["is_vocalo"]) & (df["year"] >= 2025))].copy()
voiro_df = df_filtered[~df_filtered["is_vocalo"]].copy()

# 1. 岐阜県、広島県、山口県などの動画を調査
pref_mask = voiro_df["tags"].str.contains(r"岐阜県|広島県|山口県|観光スポットおよび祭り・イベントの一覧", case=False)
pref_vids = voiro_df[pref_mask]

out = []
out.append(f"=== 都道府県・観光スポット関連動画 (全{len(pref_vids)}本) ===")
out.append(f"- 既に「旅行」タグがついているもの: {pref_vids['tags'].str.contains('旅行').sum()}本")
out.append(f"- 既に「車載」タグがついているもの: {pref_vids['tags'].str.contains('車載').sum()}本")
out.append(f"- 旅行・車載タグがついていないもの: {(~pref_vids['tags'].str.contains('旅行|車載')).sum()}本\n")

out.append("--- 旅行・車載タグなしの動画例 (上位15件) ---")
no_travel_pref = pref_vids[~pref_vids["tags"].str.contains("旅行|車載")]
for _, r in no_travel_pref.head(15).iterrows():
    out.append(f"[{r['year']}年 / {r['viewCounter']}再生] {r['title']}")
    out.append(f"  タグ: {r['tags']}")

# 2. ラジオ・雑談の調査
radio_mask = voiro_df["tags"].str.contains(r"ラジオ|雑談", case=False)
radio_vids = voiro_df[radio_mask]
out.append(f"\n=== ラジオ・雑談関連動画 (全{len(radio_vids)}本) ===")
out.append(f"- 既に「実況」タグがついているもの: {radio_vids['tags'].str.contains('実況').sum()}本")
out.append(f"- 既に「劇場」タグがついているもの: {radio_vids['tags'].str.contains('劇場').sum()}本")
out.append(f"- 実況・劇場なし: {(~radio_vids['tags'].str.contains('実況|劇場')).sum()}本\n")
for _, r in radio_vids[~radio_vids["tags"].str.contains("実況|劇場")].head(10).iterrows():
    out.append(f"[{r['year']}年 / {r['viewCounter']}再生] {r['title']}")
    out.append(f"  タグ: {r['tags']}")

# 3. ASMRの調査
asmr_mask = voiro_df["tags"].str.contains(r"ASMR|ASMROID|バイノーラル|シチュエーションボイス|耳かき", case=False)
asmr_vids = voiro_df[asmr_mask]
out.append(f"\n=== ASMR関連動画 (全{len(asmr_vids)}本) ===")
for _, r in asmr_vids.head(10).iterrows():
    out.append(f"[{r['year']}年 / {r['viewCounter']}再生] {r['title']}")
    out.append(f"  タグ: {r['tags']}")

with open("results/genre_investigation.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("Saved to results/genre_investigation.txt")
