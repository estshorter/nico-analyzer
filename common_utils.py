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
    大文字小文字を区別せずに（case-insensitive）検索します。
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
        
    # 検索用に小文字化した文字列とリストを用意
    tags_str_lower = tags_str.lower()
    tag_list_lower = [t.lower() for t in tag_list]
        
    found = []
    # 短い名前や一般的な単語と被りやすい名前は完全一致、それ以外は部分一致
    exact_match_chars = ["RIA", "朱花", "青葉", "銀芽", "金苗", "ナツ", "シロ", "ナコ", "レコ"]
    exact_match_chars_lower = [c.lower() for c in exact_match_chars]
    
    for name in character_names:
        name_lower = name.lower()
        if name_lower in exact_match_chars_lower:
            if name_lower in tag_list_lower:
                found.append(name)
        else:
            if name_lower in tags_str_lower:
                found.append(name)
    return found
