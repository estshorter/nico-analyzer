import pandas as pd
import pickle

def check_biim():
    with open('results/all_2025.pickle', 'rb') as f:
        data = pickle.load(f)['data']
    df = pd.DataFrame(data)
    df['tags'] = df['tags'].fillna('').astype(str)
    
    tags_to_check = [
        'biim兄貴リスペクト',
        'biimシステム',
        'biimリスペクト',
        'biim'
    ]
    
    print("--- Tag Counts in Raw Data (2025) ---")
    for tag in tags_to_check:
        count = df[df['tags'].str.contains(tag, case=False, na=False)].shape[0]
        print(f"{tag:20}: {count:,}")

    print("\n--- Overlap with Priority Genres ---")
    # Priority patterns from previous script
    soft_talk_include = "ソフトウェアトーク|VOICEPEAK|VOICEROID|A.I.VOICE|CeVIO|VOICEVOX|ガイノイドTalk|CoeFont|COEIROINK|結月ゆかり|紲星あかり|琴葉茜|琴葉葵|東北きりたん|ずんだもん"
    soft_talk_exclude = "VOCALOID|VOCAROID|音楽|歌うボイスロイド|CeVIOカバー曲|CeVIOオリジナル曲|歌ってみた"
    yukkuri = "ゆっくり"
    
    biim_mask = df['tags'].str.contains('biim', case=False, na=False)
    df_biim = df[biim_mask].copy()
    
    is_soft_talk = df_biim['tags'].str.contains(soft_talk_include, case=False, na=False) & ~df_biim['tags'].str.contains(soft_talk_exclude, case=False, na=False)
    is_yukkuri = df_biim['tags'].str.contains(yukkuri, case=False, na=False)
    
    print(f"Total videos with 'biim' in tags: {len(df_biim):,}")
    print(f"  - Also contains Software Talk: {is_soft_talk.sum():,}")
    print(f"  - Also contains Yukkuri     : {is_yukkuri.sum():,}")
    print(f"  - Neither (Pure biim?)      : {(~is_soft_talk & ~is_yukkuri).sum():,}")

if __name__ == "__main__":
    check_biim()
