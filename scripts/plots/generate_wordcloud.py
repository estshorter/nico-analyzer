import pickle
import pandas as pd
import MeCab
import unidic_lite
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re
import os

def load_data():
    with open('results/onboard.pickle', 'rb') as f:
        data = pickle.load(f)
    df = pd.DataFrame(data['data'])
    df['startTime'] = pd.to_datetime(df['startTime'])
    df['year'] = df['startTime'].dt.year
    return df

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
                # Ignore very common generic words to highlight "projects"
                stop_words = ['車載', '動画', 'VOICEROID', '東北', '星あかり', 'ボイロ', '紲星']
                if node.surface not in stop_words:
                    nouns.append(node.surface)
        node = node.next
    return " ".join(nouns)

def generate_wc(df, year_range, filename, title_label):
    tagger = get_tagger()
    target_df = df[df['year'].isin(year_range)]
    # Use top 1000 by viewCounter for each year in the range
    texts = []
    for year in year_range:
        year_top = target_df[target_df['year'] == year].sort_values('viewCounter', ascending=False).head(1000)
        for title in year_top['title']:
            texts.append(extract_nouns(title, tagger))
    
    combined_text = " ".join(texts)
    
    # Windows standard font
    font_path = "C:\\Windows\\Fonts\\msgothic.ttc"
    
    wc = WordCloud(
        width=800, 
        height=400, 
        background_color='white', 
        font_path=font_path,
        colormap='viridis',
        max_words=100
    ).generate(combined_text)
    
    plt.figure(figsize=(10, 5))
    plt.imshow(wc, interpolation='bilinear')
    plt.title(title_label, fontsize=15)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(f'results/{filename}.png')
    print(f"Saved {filename}.png")

if __name__ == "__main__":
    df = load_data()
    os.makedirs('results', exist_ok=True)
    
    # Early era (2015-2017)
    generate_wc(df, range(2015, 2018), "onboard_early_wc", "Onboard Early (2015-2017)")
    
    # Recent era (2023-2025)
    generate_wc(df, range(2023, 2026), "onboard_recent_wc", "Onboard Recent (2023-2025)")
