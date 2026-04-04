import pickle
import pandas as pd
from collections import Counter
import MeCab
import unidic_lite
import re

def get_tagger():
    dic_path = unidic_lite.DICDIR
    return MeCab.Tagger(f'-d "{dic_path}"')

def extract_nouns(text, tagger):
    nouns = []
    text = re.sub(r'[【】［］（）()!！?？\[\]]', ' ', text)
    node = tagger.parseToNode(text)
    while node:
        features = node.feature.split(',')
        if features[0] == '名詞':
            if len(node.surface) > 1 and not node.surface.isdigit():
                nouns.append(node.surface)
        node = node.next
    return nouns

def main():
    with open('results/onboard.pickle', 'rb') as f:
        data = pickle.load(f)
    df = pd.DataFrame(data['data'])
    df['startTime'] = pd.to_datetime(df['startTime'])
    df['year'] = df['startTime'].dt.year
    
    # 2022年以降の上位1000件
    recent_top = df[df['year'] >= 2022].sort_values('viewCounter', ascending=False).head(1000)
    
    print("=== 投稿者バイアスの検証 ===")
    owner_counts = recent_top['userId'].value_counts()
    print("\n■ 上位1000件における投稿者占有率 (Top 10):")
    for i, (oid, count) in enumerate(owner_counts.head(10).items(), 1):
        sample_title = recent_top[recent_top['userId'] == oid]['title'].iloc[0]
        print(f"{i}. Owner: {oid} - {count}件 (サンプル: {sample_title[:40]}...)")
    
    # 「信州」や特定のシリーズ名のチェック
    shinshu_series = recent_top[recent_top['title'].str.contains('信州', na=False)]
    print(f"\n■ 「信州」を含む動画: {len(shinshu_series)} / 1000 件")
    
    # バイアス除去（1人あたり最大3件までに制限）
    df_limited = recent_top.groupby('userId').head(3)
    print(f"\n■ 1人最大3件に制限後のサンプル数: {len(df_limited)} 件")
    
    tagger = get_tagger()
    all_nouns_raw = []
    for title in recent_top['title']:
        all_nouns_raw.extend(extract_nouns(title, tagger))
    
    all_nouns_limited = []
    for title in df_limited['title']:
        all_nouns_limited.extend(extract_nouns(title, tagger))
        
    raw_counter = Counter(all_nouns_raw)
    lim_counter = Counter(all_nouns_limited)
    
    print("\n■ 主要キーワードの普及度（ユニーク投稿者数）:")
    keywords = ['紹介', '記録', 'ルート', '初心者', '検証', '日帰り', '比較', '方法', '解説']
    for kw in sorted(list(set(keywords))):
        hits = recent_top[recent_top['title'].str.contains(kw, na=False)]
        u_count = hits['userId'].nunique()
        if u_count > 0:
            print(f"{kw:<6} | {len(hits):>4}件 (投稿者数: {u_count:>3}人) -> 1人平均: {len(hits)/u_count:.1f}件")
        else:
            print(f"{kw:<6} | {len(hits):>4}件 (投稿者数:   0人)")

if __name__ == "__main__":
    main()
