import pickle
import pandas as pd
import re
import sys

# Narrative and temporal indicators of series
patterns = {
    'part_style': r'(?i)part\s*(?:\d+|最終|完結|おまけ)',
    'episode_style': r'(?i)(?:第[一二三四五六七八九十\d]+|最終)(?:話|回|章|節)',
    'symbol_style': r'(?i)(?:#|No\.?|Vol\.?|vol\.?|v\.?)\s*(?:\d+|最終|last)\b',
    'bracket_style': r'[【（\(\[［](?!20[12]\d|1080|720|4k|4K)\d{1,3}[】）\)\]］]',
    'prefix_style': r'(?i)(?:第[一二三四五六七八九十\d]+[回 ]|其の[一二三四五六七八九十\d]+|その\d+(?:\.\d+)?|Phase\s*(?:\d+|last)|SS\.?\s*\d+)',
    'bare_number_style': r'[\s\-]\d{1,3}$',
    # Temporal progress indicators
    'temporal_style': r'(?i)(?:\d+|最終)\s*日目|Day\s*(?:\d+|last)',
    # Terms that strongly imply a series structure
    'narrative_style': r'(?i)(?:最終回|プロローグ|エピローグ|オープニング|エンディング|OP邱ｨ|ED邱ｨ|前回|次回)'
}

def is_series(text):
    if not isinstance(text, str): return False
    for p in patterns.values():
        if re.search(p, text): return True
    return False

def get_top_titles(df, start_year, end_year, limit=100):
    subset = df[(df['year'] >= start_year) & (df['year'] <= end_year)]
    top = subset.sort_values('viewCounter', ascending=False).head(limit)
    return top[['title', 'viewCounter', 'startTime']]

with open('results/onboard.pickle', 'rb') as f:
    data = pickle.load(f)

df = pd.DataFrame(data['data'])
df['startTime'] = pd.to_datetime(df['startTime'])
df['year'] = df['startTime'].dt.year

# 2015-2018
top_old = get_top_titles(df, 2015, 2018)
# 2022-2025
top_new = get_top_titles(df, 2022, 2025)

with open('results/top_titles_comparison.md', 'w', encoding='utf-8') as f:
    def write_md(title_df, period_label):
        f.write(f"# {period_label} 上位100件のタイトル比較\n\n")
        f.write("| 順位 | シリーズ判定 | 再生数 | タイトル |\n")
        f.write("|------|---------|------------|-------|\n")
        for i, (idx, row) in enumerate(title_df.iterrows(), 1):
            series_mark = "✅" if is_series(row['title']) else "❌"
            # Clean title for markdown table
            title = row['title'].replace('|', '｜')
            f.write(f"| {i} | {series_mark} | {row['viewCounter']:,} | {title} |\n")
        f.write("\n---\n\n")

    write_md(top_old, "2015-2018（初期）")
    write_md(top_new, "2022-2025（近年）")

print("結果を 'results/top_titles_comparison.md' に出力しました。")
