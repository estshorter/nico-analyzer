import pickle
import pandas as pd
import MeCab
import unidic_lite
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re
import os
from tqdm import tqdm

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
                stop_words = ['車載', '動画', 'VOICEROID', '東北', '星あかり', 'ボイロ', '紲星', 'ゆかり', 'あかり', 'マキ']
                if node.surface not in stop_words:
                    nouns.append(node.surface)
        node = node.next
    return " ".join(nouns)

def generate_wc_yearly(df):
    tagger = get_tagger()
    output_dir = 'results/wordclouds'
    os.makedirs(output_dir, exist_ok=True)
    
    # Analyze from 2015 to 2025
    years = sorted([y for y in df['year'].unique() if 2015 <= y <= 2025])
    
    # Windows standard font
    font_path = "C:\\Windows\\Fonts\\msgothic.ttc"
    
    for year in tqdm(years, desc="Generating yearly wordclouds"):
        year_top = df[df['year'] == year].sort_values('viewCounter', ascending=False).head(1000)
        
        texts = []
        for title in year_top['title']:
            texts.append(extract_nouns(title, tagger))
        
        combined_text = " ".join(texts)
        if not combined_text.strip():
            continue
            
        wc = WordCloud(
            width=800, 
            height=400, 
            background_color='white', 
            font_path=font_path,
            colormap='plasma', # Different colormap for variety
            max_words=80
        ).generate(combined_text)
        
        plt.figure(figsize=(10, 5))
        plt.imshow(wc, interpolation='bilinear')
        plt.title(f"Onboard Video Trends - {year}", fontsize=20)
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(f'{output_dir}/onboard_wc_{year}.png')
        plt.close() # Close to free memory

if __name__ == "__main__":
    df = load_data()
    generate_wc_yearly(df)
    print("\nYearly wordclouds saved to results/wordclouds/")
