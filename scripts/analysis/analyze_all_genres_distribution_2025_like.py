# -*- coding: utf-8 -*-
import pandas as pd
import pickle
import numpy as np
import os
import time

def classify_genres(df):
    # Classification logic synchronized with categorize_ranking.py
    df["tags"] = df["tags"].fillna("").astype(str)
    
    re_no_are = "例のアレ|淫夢|レスリングシリーズ|クッキー☆|拓也|ホモと|ゼERO|頭がパーン|エア本さん|必須アモト酸|変態糞親父|BME|恒心教|ハセカラ|オウム真理教"
    soft_talk_include = "ソフトウェアトーク|VOICEPEAK|VOICEROID|A.I.VOICE|CeVIO|VOICEVOX|ガイノイドTalk|CoeFont|COEIROINK|結月ゆかり|紲星あかり|琴葉茜|琴葉葵|東北きりたん|ずんだもん"
    soft_talk_exclude = "VOCALOID|VOCAROID|音楽|歌うボイスロイド|CeVIOカバー曲|CeVIOオリジナル曲|歌ってみた|VOICEPEAKオリジナル曲|音MAD|替え歌|踊ってみた"
    yukkuri = "ゆっくり"
    vocaloid_include = "VOCALOID|ボカロ|初音ミク|UTAU|Synthesizer_V|SynthesizerV|ボカコレ|VoiSona|NEUTRINO|VOICEPEAKオリジナル曲"
    cevio_music_limit = "VOCALOID|VOCAROID|音楽|歌うボイスロイド|CeVIOカバー曲|CeVIOオリジナル曲|歌ってみた"
    
    # Define conditions for each genre
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
        ('フィッシング', lambda d: d['tags'].str.contains("フィッシング|釣り", case=False, na=False)),
        ('ASMR', lambda d: d['tags'].str.contains("ASMR", case=False, na=False)),
    ]

    masks = {}
    for name, condition in genre_conditions:
        masks[name] = condition(df)
        
    # Special logic for Game and Music (Other)
    masks['ゲーム（肉声・字幕）'] = df['tags'].apply(lambda t: '実況プレイ動画' in t.split()) & ~masks['ボイロ'] & ~masks['ゆっくり']
    
    any_so_far_mask = pd.Series(False, index=df.index)
    for name in masks:
        any_so_far_mask |= masks[name]
        
    masks['ゲーム（その他）'] = df['tags'].apply(lambda t: 'ゲーム' in t.split()) & ~any_so_far_mask
    any_so_far_mask |= masks['ゲーム（その他）']
    
    music_cond = df['tags'].str.contains(r"(?:^| )音楽(?:$| )", regex=True, case=False, na=False)
    masks['音楽（その他）'] = music_cond & ~any_so_far_mask

    # Boiro sub-genres
    boiro_subgenres = {
        'ゲーム': r"実況プレイ",
        '劇場': r"劇場",
        '解説': r"解説",
        'キッチン': r"キッチン",
        'グルメ': r"グルメ",
        '車載': r"車載",
        '旅行': r"旅行",
        'キャンプ': r"キャンプ",
        '例のアレ': r"淫夢|例のアレ|拓也",
        'フィッシング': r"フィッシング",
        'ASMR': r"ASMR",
        'ボイロAV': r"ボイロAV"
    }
    
    boiro_subgenre_masks = {}
    boiro_mask = masks['ボイロ']
    for sub_name, pattern in boiro_subgenres.items():
        boiro_subgenre_masks[sub_name] = boiro_mask & df['tags'].str.contains(pattern, case=False, na=False)
        
    return masks, boiro_subgenre_masks

def analyze_genres():
    print("Loading data from results/all_2025.pickle...")
    if not os.path.exists("results/all_2025.pickle"):
        print("Error: results/all_2025.pickle not found.")
        return

    with open("results/all_2025.pickle", "rb") as f:
        raw_data = pickle.load(f)

    df = pd.DataFrame(raw_data["data"])
    df["likeCounter"] = pd.to_numeric(df["likeCounter"], errors="coerce").fillna(0)
    total_count = len(df)
    total_likes = df['likeCounter'].sum()

    print(f"Total videos: {total_count:,}")

    masks, boiro_subgenre_masks = classify_genres(df)
    
    all_genres_list = [
        '公式アニメ', '公式特撮', '非公式アニメ', 'トリッカル', '手子商事開発', '狩猟', '遊戯王',
        'ボイロ', 'ゆっくり', 'VOCALOID', '例のアレ', 
        '音MAD', '歌ってみた', 'biim', 'ゲーム（肉声・字幕）', 'ゲーム（その他）',
        'MMD', '踊ってみた', 'VTuber', 'TRPG', 'RTA（純粋）', 'ニコニコ技術部', '音楽（その他）',
        'フィッシング', 'ASMR'
    ]

    any_genre_mask = pd.Series(False, index=df.index)
    for g in all_genres_list:
        any_genre_mask |= masks[g]
    
    genre_results = []
    for g in all_genres_list:
        mask = masks[g]
        count = mask.sum()
        likes = df.loc[mask, 'likeCounter'].sum()
        genre_results.append({
            'ジャンル': g,
            '動画数': count,
            '投稿数シェア (%)': round(count / total_count * 100, 2),
            'いいね数': int(likes),
            'いいね数シェア (%)': round(likes / total_likes * 100, 2)
        })

    others_mask = ~any_genre_mask
    others_count = others_mask.sum()
    others_likes = df.loc[others_mask, 'likeCounter'].sum()
    genre_results.append({
        'ジャンル': 'その他',
        '動画数': others_count,
        '投稿数シェア (%)': round(others_count / total_count * 100, 2),
        'いいね数': int(others_likes),
        'いいね数シェア (%)': round(others_likes / total_likes * 100, 2)
    })
    
    stats = pd.DataFrame(genre_results)
    
    # Sort by likes_share (%) descending, keeping 'その他' at the bottom
    others_row = stats[stats['ジャンル'] == 'その他']
    main_genres = stats[stats['ジャンル'] != 'その他'].sort_values('いいね数シェア (%)', ascending=False)
    stats = pd.concat([main_genres, others_row])
    
    # Boiro sub-genre breakdown
    boiro_total = masks['ボイロ'].sum()
    boiro_total_likes = df.loc[masks['ボイロ'], 'likeCounter'].sum()
    
    subgenre_stats = []
    boiro_any_subgenre_mask = pd.Series(False, index=df.index)
    for name, mask in boiro_subgenre_masks.items():
        count = mask.sum()
        likes = df.loc[mask, 'likeCounter'].sum()
        boiro_any_subgenre_mask |= mask
        subgenre_stats.append({
            'サブジャンル': name,
            '動画数': count,
            '投稿数シェア (%)': round(count / boiro_total * 100, 1) if boiro_total > 0 else 0,
            'いいね数': int(likes),
            'いいね数シェア (%)': round(likes / boiro_total_likes * 100, 1) if boiro_total_likes > 0 else 0
        })
    
    boiro_others_mask = masks['ボイロ'] & ~boiro_any_subgenre_mask
    others_count = boiro_others_mask.sum()
    others_likes = df.loc[boiro_others_mask, 'likeCounter'].sum()
    subgenre_stats.append({
        'サブジャンル': 'その他 (分類不能)',
        '動画数': others_count,
        '投稿数シェア (%)': round(others_count / boiro_total * 100, 1) if boiro_total > 0 else 0,
        'いいね数': int(others_likes),
        'いいね数シェア (%)': round(others_likes / boiro_total_likes * 100, 1) if boiro_total_likes > 0 else 0
    })
    
    subgenre_df = pd.DataFrame(subgenre_stats)
    # Sort by likes descending
    subgenre_df = subgenre_df.sort_values('いいね数', ascending=False)

    # Export Boiro Others to CSV
    if boiro_others_mask.any():
        boiro_others_df = df[boiro_others_mask].copy()
        # Add rank based on likes
        boiro_others_df = boiro_others_df.sort_values('likeCounter', ascending=False)
        boiro_others_df['rank'] = range(1, len(boiro_others_df) + 1)
        
        # Get genres for these videos (main genres)
        def get_main_genres(row_idx):
            matched = [g for g in all_genres_list if masks[g][row_idx]]
            return ', '.join(matched) if matched else 'その他'
        
        boiro_others_df['genre'] = [get_main_genres(i) for i in boiro_others_df.index]
        
        boiro_others_csv_path = 'results/genre_distribution_2025_boiro_others_like.csv'
        columns_to_export = ['rank', 'contentId', 'title', 'genre', 'tags', 'likeCounter']
        boiro_others_df[columns_to_export].to_csv(boiro_others_csv_path, index=False, encoding='utf-8-sig')
        print(f"Saved 2025 Boiro 'Others' detailed list to {boiro_others_csv_path}")

    # Save Output
    output_path = "results/genre_distribution_2025_like.md"
    os.makedirs('results', exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# 2025年 ニコニコ動画 ジャンル別投稿数・いいね数割合 (重複あり)\n\n")
        f.write(f"データ元: `results/all_2025.pickle` (2025年投稿動画)\n\n")
        f.write("※重複ありで集計しています。\n\n")
        f.write(stats.to_markdown(index=False))
        f.write("\n\n")
        f.write(f"- **総投稿数 (ユニーク)**: {total_count:,}\n")
        f.write(f"- **総いいね数 (合計)**: {total_likes:,}\n\n")
        
        f.write("## ボイロ詳細ジャンル内訳 (2025年通年)\n\n")
        f.write(subgenre_df.to_markdown(index=False))
        f.write("\n\n")
        f.write(f"- **ボイロ総投稿数**: {boiro_total:,}\n")
        f.write(f"- **ボイロ総いいね数**: {boiro_total_likes:,}\n")

    print(f"\nResults saved to {output_path}")

if __name__ == "__main__":
    analyze_genres()
