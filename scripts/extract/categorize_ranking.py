import requests
import re
import html
import pandas as pd
import time
from tqdm import tqdm
from bs4 import BeautifulSoup
import os
import argparse

def get_top_100_video_ids():
    url = "https://www.nicovideo.jp/ranking"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    unescaped_text = html.unescape(response.text)
    
    matches = re.finditer(r'"id":"((?:sm|so|nm)\d+)"', unescaped_text)
    unique_ids = []
    seen = set()
    for match in matches:
        vid = match.group(1)
        if vid not in seen:
            seen.add(vid)
            unique_ids.append(vid)
            
    return unique_ids[:100]

def fetch_video_metadata(video_id):
    url = f"https://ext.nicovideo.jp/api/getthumbinfo/{video_id}"
    try:
        response = requests.get(url, timeout=10.0)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "xml")
        
        if soup.find("error"):
            return {"contentId": video_id, "title": "", "tags": "", "viewCounter": 0}
            
        tags = [t.text for t in soup.find_all("tag")]
        view_counter = soup.find("view_counter")
        view_count = int(view_counter.text) if view_counter else 0
        title = soup.find("title").text if soup.find("title") else ""
        
        return {
            "contentId": video_id,
            "title": title,
            "tags": " ".join(tags),
            "viewCounter": view_count
        }
    except Exception as e:
        print(f"Error fetching metadata for {video_id}: {e}")
        
    return {"contentId": video_id, "title": "", "tags": "", "viewCounter": 0}

def classify_genres(df):
    df["tags"] = df["tags"].fillna("").astype(str)
    
    re_no_are = "例のアレ|淫夢|レスリングシリーズ|クッキー☆|拓也|ホモと"
    soft_talk_include = "ソフトウェアトーク|VOICEPEAK|VOICEROID|A.I.VOICE|CeVIO|VOICEVOX|ガイノイドTalk|CoeFont|COEIROINK|結月ゆかり|紲星あかり|琴葉茜|琴葉葵|東北きりたん|ずんだもん|弦巻マキ"
    soft_talk_exclude = "VOCALOID|VOCAROID|音楽|歌うボイスロイド|CeVIOカバー曲|CeVIOオリジナル曲|歌ってみた|VOICEPEAKオリジナル曲|音MAD|替え歌|踊ってみた"
    yukkuri = "ゆっくり"
    vocaloid_include = "VOCALOID|ボカロ|初音ミク|UTAU|Synthesizer_V|SynthesizerV|ボカコレ|VoiSona|NEUTRINO|VOICEPEAKオリジナル曲"
    cevio_music_limit = "VOCALOID|VOCAROID|音楽|歌うボイスロイド|CeVIOカバー曲|CeVIOオリジナル曲|歌ってみた"
    
    genre_conditions = [
        ('公式アニメ', lambda d: d['contentId'].str.startswith('so') & ((d['tags'].str.contains(r"\d{4}年(?:春|夏|秋|冬)アニメ", case=False, na=False)) | d['tags'].apply(lambda t: 'dアニメストア' in t.split()))),
        ('公式特撮', lambda d: d['tags'].str.contains("特撮", case=False, na=False) & d['contentId'].str.startswith('so')),
        ('非公式アニメ', lambda d: d['tags'].apply(lambda t: 'アニメ' in t.split()) & ~d['contentId'].str.startswith('so')),
        ('トリッカル', lambda d: d['tags'].str.contains("トリッカル", case=False, na=False)),
        ('手子商事開発', lambda d: d['tags'].str.contains("手子商事開発", case=False, na=False)),
        ('狩猟', lambda d: d['tags'].str.contains("狩猟", case=False, na=False)),
        ('遊戯王', lambda d: d['tags'].str.contains("遊戯王", case=False, na=False)),
        ('例のアレ', lambda d: d['tags'].str.contains(re_no_are, case=False, na=False)),
        ('ボイロ', lambda d: d['tags'].str.contains(soft_talk_include, case=False, na=False) & 
                                     ~d['tags'].str.contains(soft_talk_exclude, case=False, na=False)),
        ('ゆっくり', lambda d: d['tags'].str.contains(yukkuri, case=False, na=False)),
        ('VOCALOID', lambda d: d['tags'].str.contains(vocaloid_include, case=False, na=False) | 
                               (d['tags'].str.contains("CeVIO", case=False, na=False) & 
                                d['tags'].str.contains(cevio_music_limit, case=False, na=False))),
        ('biim', lambda d: d['tags'].str.contains("biim兄貴", case=False, na=False)),
        ('RTA（純粋）', lambda d: d['tags'].str.contains("RTA", case=False, na=False) & ~d['tags'].str.contains("biim兄貴", case=False, na=False)),
        ('TRPG', lambda d: d['tags'].str.contains("TRPG", case=False, na=False)),
        ('VTuber', lambda d: d['tags'].str.contains("VTuber", case=False, na=False)),
        ('歌ってみた', lambda d: d['tags'].str.contains("歌ってみた", case=False, na=False)),
        ('踊ってみた', lambda d: d['tags'].str.contains("踊ってみた", case=False, na=False)),
        ('ニコニコ技術部', lambda d: d['tags'].str.contains("ニコニコ技術部", case=False, na=False)),
        ('MMD', lambda d: d['tags'].str.contains("MMD", case=False, na=False)),
        ('音MAD', lambda d: d['tags'].str.contains("音MAD", case=False, na=False)),
        ('ASMR', lambda d: d['tags'].str.contains("ASMR", case=False, na=False)),
        # ('料理', lambda d: d['tags'].str.contains("料理", case=False, na=False)),
        ('旅行', lambda d: d['tags'].str.contains("旅行", case=False, na=False)),
        ('交通事故', lambda d: d['tags'].str.contains("交通事故", case=False, na=False)),
    ]

    masks = {}
    for name, condition in genre_conditions:
        masks[name] = condition(df)
        
    masks['ゲーム（肉声・字幕）'] = df['tags'].apply(lambda t: '実況プレイ動画' in t.split()) & ~masks['ボイロ'] & ~masks['ゆっくり']
    
    any_so_far_mask = pd.Series(False, index=df.index)
    for name in masks:
        any_so_far_mask |= masks[name]
        
    masks['ゲーム（その他）'] = df['tags'].apply(lambda t: 'ゲーム' in t.split()) & ~any_so_far_mask
    any_so_far_mask |= masks['ゲーム（その他）']
    
    music_cond = df['tags'].str.contains(r"(?:^| )音楽(?:$| )", regex=True, case=False, na=False)
    masks['音楽（その他）'] = music_cond & ~any_so_far_mask

    all_genres_list = [
        '公式アニメ', '公式特撮', '非公式アニメ', 'トリッカル', '手子商事開発', '狩猟', '遊戯王',
        'ボイロ', 'ゆっくり', 'VOCALOID', '例のアレ', 
        '音MAD', '歌ってみた', 'biim', 'ゲーム（肉声・字幕）', 'ゲーム（その他）',
        'MMD', '踊ってみた', 'VTuber', 'TRPG', 'RTA（純粋）', 'ニコニコ技術部', '音楽（その他）',
        'ASMR',
    ]

    def get_matched_genres(row_idx):
        matched = [g for g in all_genres_list if masks[g][row_idx]]
        if not matched:
            return ['その他']
        return matched

    df['genre_list'] = [get_matched_genres(i) for i in range(len(df))]
    df['genre'] = df['genre_list'].apply(lambda x: ', '.join(x))

    boiro_subgenres = {
        'ゲーム': r"実況プレイ|ドラゴンボールザブレイカーズ",
        '劇場': r"劇場",
        '解説': r"解説",
        'キッチン': r"キッチン",
        'グルメ': r"グルメ",
        '例のアレ': r"淫夢|例のアレ|拓也",
        '車載': r"車載",
        '旅行': r"旅行",
        'キャンプ': r"キャンプ",
        'フィッシング': r"フィッシング|釣り",
        'ASMR': r"ASMR",
        'ボイロAV': r"ボイロAV|VOICEROID_AV"
    }
    
    boiro_subgenre_masks = {}
    boiro_mask = masks['ボイロ']
    for sub_name, pattern in boiro_subgenres.items():
        boiro_subgenre_masks[sub_name] = boiro_mask & df['tags'].str.contains(pattern, case=False, na=False)
        
    return df, masks, boiro_subgenre_masks

def main():
    parser = argparse.ArgumentParser(description='ニコニコ動画ランキングのジャンル分け・集計を行います。')
    parser.add_argument('input_csv', nargs='?', help='入力するCSVファイルのパス（省略時は現在のランキングをスクレイピング）')
    args = parser.parse_args()

    if args.input_csv:
        print(f"Reading CSV from {args.input_csv}...")
        df = pd.read_csv(args.input_csv)
        # 必要なカラムのチェックと補完
        if 'contentId' not in df.columns:
            print("Error: 'contentId' column is missing in CSV.")
            return
        if 'tags' not in df.columns:
            print("Error: 'tags' column is missing in CSV.")
            return
        if 'title' not in df.columns:
            df['title'] = ""
        if 'viewCounter' not in df.columns:
            df['viewCounter'] = 0
        if 'rank' not in df.columns:
            df['rank'] = range(1, len(df) + 1)
    else:
        print("Scraping top 100 video IDs from Nicovideo ranking...")
        video_ids = get_top_100_video_ids()
        print(f"Scraped {len(video_ids)} IDs.")
        
        print("Fetching video metadata (tags, views) via API...")
        data = []
        for i, vid in enumerate(tqdm(video_ids)):
            meta = fetch_video_metadata(vid)
            meta["rank"] = i + 1
            data.append(meta)
            time.sleep(0.3)
            
        df = pd.DataFrame(data)
    
    print("Classifying genres (with overlaps)...")
    df, masks, boiro_subgenre_masks = classify_genres(df)
    
    all_genres_list = [
        '公式アニメ', '公式特撮', '非公式アニメ', 'トリッカル', '手子商事開発', '狩猟', '遊戯王',
        'ボイロ', 'ゆっくり', 'VOCALOID', '例のアレ', 
        '音MAD', '歌ってみた', 'biim', 'ゲーム（肉声・字幕）', 'ゲーム（その他）',
        'MMD', '踊ってみた', 'VTuber', 'TRPG', 'RTA（純粋）', 'ニコニコ技術部', '音楽（その他）',
        'ASMR'
    ]

    any_genre_mask = pd.Series(False, index=df.index)
    for g in all_genres_list:
        any_genre_mask |= masks[g]
    
    stats_data = []
    for g in all_genres_list:
        count = masks[g].sum()
        stats_data.append({
            'ジャンル': g,
            '動画数': count,
            'シェア (%)': round(count / len(df) * 100, 2)
        })
    
    others_count = (~any_genre_mask).sum()
    stats_data.append({
        'ジャンル': 'その他',
        '動画数': others_count,
        'シェア (%)': round(others_count / len(df) * 100, 2)
    })
    
    stats = pd.DataFrame(stats_data)
    others_row = stats[stats['ジャンル'] == 'その他']
    main_genres = stats[stats['ジャンル'] != 'その他'].sort_values('シェア (%)', ascending=False)
    stats = pd.concat([main_genres, others_row])
    
    os.makedirs('results', exist_ok=True)
    
    if args.input_csv:
        base_name = os.path.splitext(os.path.basename(args.input_csv))[0]
        timestamp = f"reclassified_{base_name}"
    else:
        timestamp = time.strftime("%Y%m%d_%H")
    
    summary_path = f'results/ranking_category_summary_{timestamp}.md'
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(f"# ニコニコ動画 ジャンル別分布分析 ({timestamp})\n\n")
        if args.input_csv:
            f.write(f"ソースファイル: {args.input_csv}\n\n")
        f.write("※重複ありで集計しています（1つの動画が複数のジャンルにカウントされる場合があります）。\n")
        f.write(f"※シェア(%)は全動画数({len(df)}件)に対する割合です。\n\n")
        f.write(stats[stats['動画数'] > 0].to_markdown(index=False))
        f.write("\n\n")

        f.write("## ボイロ詳細ジャンル内訳\n\n")
        
        # Sort subgenres by count descending, then add others and total
        subgenre_stats_list = []
        boiro_any_subgenre_mask = pd.Series(False, index=df.index)
        boiro_total = masks['ボイロ'].sum()
        for name, mask in boiro_subgenre_masks.items():
            count = mask.sum()
            boiro_any_subgenre_mask |= mask
            subgenre_stats_list.append({'サブジャンル': name, '動画数': count})
        
        # Sort by count
        subgenre_stats_list.sort(key=lambda x: x['動画数'], reverse=True)
        
        # Add 'Share (%)' after sorting
        for item in subgenre_stats_list:
            share = round(item['動画数'] / boiro_total * 100, 1) if boiro_total > 0 else 0
            item['シェア (%)'] = f"{share}%"
            
        # Add Others
        boiro_others_mask = masks['ボイロ'] & ~boiro_any_subgenre_mask
        others_count = boiro_others_mask.sum()
        others_share = round(others_count / boiro_total * 100, 1) if boiro_total > 0 else 0
        subgenre_stats_list.append({'サブジャンル': 'その他 (分類不能)', '動画数': others_count, 'シェア (%)': f"{others_share}%"})
        
        # Add Total
        subgenre_stats_list.append({'サブジャンル': '**合計 (ボイロ総数)**', '動画数': f"**{boiro_total}**", 'シェア (%)': '**100.0%**'})
        
        subgenre_df = pd.DataFrame(subgenre_stats_list)
        f.write(subgenre_df.to_markdown(index=False))
        f.write("\n\n")
        
        if boiro_others_mask.any():
            boiro_others_df = df[boiro_others_mask]
            f.write("## ボイロその他詳細 (分類不能分)\n\n")
            if 'viewCounter' in boiro_others_df.columns and boiro_others_df['viewCounter'].sum() > 0:
                f.write(boiro_others_df[['rank', 'contentId', 'title', 'viewCounter']].to_markdown(index=False))
            else:
                f.write(boiro_others_df[['rank', 'contentId', 'title']].to_markdown(index=False))
            f.write("\n\n")
            
            # Export Boiro Others to CSV
            boiro_others_csv_path = f'results/ranking_boiro_others_{timestamp}.csv'
            boiro_others_df[['rank', 'contentId', 'title', 'genre', 'tags']].to_csv(boiro_others_csv_path, index=False, encoding='utf-8-sig')
            print(f"Saved Boiro 'Others' detailed list to {boiro_others_csv_path}")
    
    detailed_df = df[['rank', 'contentId', 'title', 'genre', 'tags']]
    detailed_path = f'results/ranking_detailed_list_{timestamp}.csv'
    detailed_df.to_csv(detailed_path, index=False, encoding='utf-8-sig')
    print(f"Saved detailed list to {detailed_path}")
    print(f"Summary saved to {summary_path}")
    
if __name__ == "__main__":
    main()
