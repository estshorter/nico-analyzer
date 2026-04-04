import pickle
import pandas as pd

def main():
    with open('results/onboard.pickle', 'rb') as f:
        data = pickle.load(f)
    df = pd.DataFrame(data['data'])
    df['startTime'] = pd.to_datetime(df['startTime'])
    df['year'] = df['startTime'].dt.year
    
    # 初期 (2015-2018)
    early = df[(df['year'] >= 2015) & (df['year'] <= 2018)]
    early_top = early.sort_values('viewCounter', ascending=False).head(1000)
    
    # 「Part」「ツーリング」「北海道」などの記録・日記的なものを抽出
    early_samples = early_top[early_top['title'].str.contains('Part|ツーリング|北海道', na=False, case=False)]
    early_samples = early_samples.drop_duplicates(subset=['userId']).head(10) # 色々な投稿者から抽出

    output_lines = []
    output_lines.append("=== 初期 (2015-2018): 「行動の記録・日記」中心のタイトル ===")
    for _, row in early_samples.iterrows():
        output_lines.append(f"[{row['contentId']}] {row['title']}")

    output_lines.append("\n")

    # 近年 (2022-2025)
    recent = df[(df['year'] >= 2022) & (df['year'] <= 2025)]
    recent_top = recent.sort_values('viewCounter', ascending=False).head(1000)
    
    # 「ルート」「紹介」「日帰り」など情報提供・具体化されたものを抽出
    recent_samples = recent_top[recent_top['title'].str.contains('ルート|紹介|日帰り', na=False)]
    recent_samples = recent_samples.drop_duplicates(subset=['userId']).head(10) # 色々な投稿者から抽出

    output_lines.append("=== 近年 (2022-2025): 「視聴者に何を見せるか（情報提供）」が具体化されたタイトル ===")
    for _, row in recent_samples.iterrows():
        output_lines.append(f"[{row['contentId']}] {row['title']}")

    with open('titles_sample.md', 'w', encoding='utf-8') as f:
        f.write("\n".join(output_lines))

if __name__ == "__main__":
    main()
