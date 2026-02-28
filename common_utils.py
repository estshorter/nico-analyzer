import pandas as pd

def filter_software_talk(df: pd.DataFrame) -> pd.DataFrame:
    """
    ソフトウェアトークのデータから、歌唱系（VOCALOID等）の動画を除外するフィルタ。
    analyzer.py, character_analyzer.py 等で共通利用されます。
    """
    if df is None or df.empty:
        return df
    
    before_count = len(df)
    # VOCALOID関連を除外（歌唱系が混じるため）
    filter_pattern = "VOCALOID|VOCAROID|音楽|歌うボイスロイド|CeVIOカバー曲|歌ってみた"
    df = df[~df["tags"].astype(str).str.contains(filter_pattern, case=False, na=False)]
    removed_count = before_count - len(df)
    
    if removed_count > 0:
        print(f"Filtered out {removed_count} VOCALOID/VOCAROID/Music videos.")
    
    return df

def find_characters(tags, character_names):
    """
    動画のタグからキャラクターを抽出する共通ロジック。
    """
    if not tags:
        return []
    if isinstance(tags, str):
        tags_str = tags
        tag_list = tags.split()
    elif isinstance(tags, list):
        tags_str = " ".join(tags)
        tag_list = tags
    else:
        return []
        
    found = []
    # 短い名前や一般的な単語と被りやすい名前は完全一致、それ以外は部分一致
    exact_match_chars = ["RIA", "朱花", "青葉", "銀芽", "金苗", "ナツ", "シロ", "ナコ", "レコ"]
    for name in character_names:
        if name in exact_match_chars:
            if name in tag_list:
                found.append(name)
        else:
            if name in tags_str:
                found.append(name)
    return found
