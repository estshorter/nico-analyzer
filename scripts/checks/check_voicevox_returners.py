import pickle
import pandas as pd
from pathlib import Path
from common_utils import filter_software_talk

pickle_path = Path("results/software_talk.pickle")
with open(pickle_path, "rb") as f:
    recv = pickle.load(f)

df = pd.json_normalize(recv["data"])
df = filter_software_talk(df)
df["startTime"] = pd.to_datetime(df["startTime"])
df = df.sort_values("startTime", ignore_index=True)
df.fillna({"userId": 0}, inplace=True)
df["userId"] = df["userId"].astype("uint64")
df = df[df["userId"] != 0].copy()
df = df[df["startTime"].dt.year <= 2025].copy()

df["overall_prev_startTime"] = df.groupby("userId")["startTime"].shift(1)
df["year"] = df["startTime"].dt.year
df["blank_days"] = (df["startTime"] - df["overall_prev_startTime"]).dt.total_seconds() / 86400.0

# BUG FIX: Use drop_duplicates to reliably get the exact first row per year/user without skipping nulls
first_posts_in_year = df.drop_duplicates(subset=["year", "userId"], keep="first").copy()

# 復帰判定
first_posts_in_year["is_returner"] = (first_posts_in_year["blank_days"] > 365)
returners = first_posts_in_year[first_posts_in_year["is_returner"]].copy()

# VOICEVOX利用判定
vv_tags = [
    "VOICEVOX", "ずんだもん", "四国めたん", "春日部つむぎ", "雨晴はう", "波音リツ", "玄野武宏",
    "白上虎太郎", "青山龍星", "冥鳴ひまり", "九州そら", "もち子さん", "剣崎雌雄", "whitecul",
    "後鬼", "no.7", "ちび式じい", "櫻歌ミコ", "小夜/sayo", "ナースロボ_タイプt", "†聖騎士紅桜†",
    "雀松朱司", "麒ヶ島宗麟", "春歌ナナ", "猫使アル", "猫使ビィ", "中国うさぎ", "あいえるたん",
    "満別花丸", "琴詠ニア", "voidoll", "ぞん子", "中部つるぎ", "離途", "黒沢冴白", "ユーレイちゃん", "あんこもん"
]
def uses_vv(tags_str):
    if not isinstance(tags_str, str):
        return False
    tags_str = tags_str.lower()
    return any(t.lower() in tags_str for t in vv_tags)

returners["uses_vv"] = returners["tags"].astype(str).apply(uses_vv)

for y in [2022, 2023, 2024, 2025]:
    ret_y = returners[returners["year"] == y]
    vv_ret_y = ret_y[ret_y["uses_vv"]]
    if len(ret_y) > 0:
        ratio = len(vv_ret_y) / len(ret_y) * 100
        print(f"{y}: 復帰者 {len(ret_y)}人中、VOICEVOX利用は {len(vv_ret_y)}人 ({ratio:.1f}%)")
