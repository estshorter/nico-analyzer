import pickle
import pandas as pd
from datetime import datetime
import MeCab
import unidic_lite
from collections import Counter
import re

def load_data():
    with open('results/onboard.pickle', 'rb') as f:
        data = pickle.load(f)
    df = pd.DataFrame(data['data'])
    df['startTime'] = pd.to_datetime(df['startTime'])
    df['year'] = df['startTime'].dt.year
    return df

def get_tagger():
    # unidic-lite dictionary path
    dic_path = unidic_lite.DICDIR
    return MeCab.Tagger(f'-d "{dic_path}"')

def extract_nouns(text, tagger):
    nouns = []
    # Clean text: remove symbols
    text = re.sub(r'[【】［］（）()!！?？\[\]]', ' ', text)
    node = tagger.parseToNode(text)
    while node:
        # Check for nouns
        features = node.feature.split(',')
        if features[0] == '名詞':
            # Ignore single characters and simple numbers
            if len(node.surface) > 1 and not node.surface.isdigit():
                nouns.append(node.surface)
        node = node.next
    return nouns

def analyze_onboard_trends(df):
    tagger = get_tagger()
    report = []
    report.append("# Onboard Video Trend Analysis Report\n")
    report.append("## Hypothesis 2: Shift to Project-Oriented (Mecab Analysis)\n")
    
    years = sorted([y for y in df['year'].unique() if 2015 <= y <= 2025])
    
    trend_data = []
    for year in years:
        year_df = df[df['year'] == year]
        top_1000 = year_df.sort_values('viewCounter', ascending=False).head(1000)
        
        all_nouns = []
        for title in top_1000['title']:
            all_nouns.extend(extract_nouns(title, tagger))
        
        counter = Counter(all_nouns)
        common_words = [f"{word}({count})" for word, count in counter.most_common(15)]
        
        trend_data.append({
            'year': year,
            'top_nouns': ", ".join(common_words)
        })
    
    res_df = pd.DataFrame(trend_data)
    report.append(res_df.to_markdown(index=False))
    
    report.append("\n## Project-Oriented Specific Keyword Frequency (Mecab-based)\n")
    
    project_kws = ['検証', '理由', '比較', '解説', '紹介', '方法', '記録', '失敗', '成功', '徹底']
    kw_stats = []
    for year in years:
        year_df = df[df['year'] == year]
        top_1000 = year_df.sort_values('viewCounter', ascending=False).head(1000)
        
        row = {'year': year}
        for kw in project_kws:
            count = top_1000['title'].str.contains(kw).sum()
            row[kw] = count / len(top_1000)
        kw_stats.append(row)
    
    kw_df = pd.DataFrame(kw_stats)
    report.append(kw_df.to_markdown(index=False))

    with open('results/onboard_analysis_report.md', 'w', encoding='utf-8') as f:
        f.write("\n".join(report))
    print("Report saved to results/onboard_analysis_report.md")

if __name__ == "__main__":
    df = load_data()
    analyze_onboard_trends(df)
