# -*- coding: utf-8 -*-
import pandas as pd
import pickle
import numpy as np
import os

def analyze_genres():
    print("Loading data from results/all_2025.pickle...")
    if not os.path.exists("results/all_2025.pickle"):
        print("Error: results/all_2025.pickle not found.")
        return

    with open("results/all_2025.pickle", "rb") as f:
        raw_data = pickle.load(f)

    # The data is a dict with keys ['meta', 'data'], where 'data' is a list of dicts
    df = pd.DataFrame(raw_data["data"])

    print(f"Total videos (unfiltered): {len(df):,}")

    # Pre-processing
    df["tags"] = df["tags"].fillna("").astype(str)
    df["viewCounter"] = pd.to_numeric(df["viewCounter"], errors="coerce").fillna(0)

    # Filter for videos with 10000+ views
    threshold = 10000
    total_count_unfiltered = len(df)
    percentile_rank = (df["viewCounter"] < threshold).mean() * 100
    top_percentage = 100 - percentile_rank
    
    print(f"Fixed Threshold: {threshold} views")
    print(f"10000 views is at the {percentile_rank:.2f}th percentile (Top {top_percentage:.2f}%)")
    
    df = df[df["viewCounter"] >= threshold].copy()
    print(f"Total videos (10000+ views): {len(df):,}")

    # Define Genres and their patterns based on docs/ジャンル区分.md
    
    # 1. 例のアレ
    re_no_are = "例のアレ|淫夢|レスリングシリーズ|クッキー☆|拓也"
    
    # 2. ソフトウェアトーク
    # Includes CeVIO but excludes musical CeVIO/VOCALOID
    soft_talk_include = "ソフトウェアトーク|VOICEPEAK|VOICEROID|A.I.VOICE|CeVIO|VOICEVOX|ガイノイドTalk|CoeFont|COEIROINK|結月ゆかり|紲星あかり|琴葉茜|琴葉葵|東北きりたん|ずんだもん"
    soft_talk_exclude = "VOCALOID|VOCAROID|音楽|歌うボイスロイド|CeVIOカバー曲|CeVIOオリジナル曲|歌ってみた"
    
    # 3. ゆっくり
    yukkuri = "ゆっくり"
    
    # 4. VOCALOID (合成音声楽曲全般)
    vocaloid_include = "VOCALOID|ボカロ|初音ミク|UTAU|Synthesizer_V|SynthesizerV|ボカコレ|VoiSona|NEUTRINO"
    cevio_music_limit = "VOCALOID|VOCAROID|音楽|歌うボイスロイド|CeVIOカバー曲|CeVIOオリジナル曲|歌ってみた"
    
    priority_genres = [
        ('例のアレ', lambda d: d['tags'].str.contains(re_no_are, case=False, na=False)),
        ('ソフトウェアトーク', lambda d: d['tags'].str.contains(soft_talk_include, case=False, na=False) & 
                                     ~d['tags'].str.contains(soft_talk_exclude, case=False, na=False)),
        ('ゆっくり', lambda d: d['tags'].str.contains(yukkuri, case=False, na=False)),
        ('VOCALOID', lambda d: d['tags'].str.contains(vocaloid_include, case=False, na=False) | 
                               (d['tags'].str.contains("CeVIO", case=False, na=False) & 
                                d['tags'].str.contains(cevio_music_limit, case=False, na=False))),
        ('biim兄貴リスペクト OR biim兄貴', lambda d: d['tags'].str.contains("biim兄貴", case=False, na=False)),
        ('RTA（純粋）', lambda d: d['tags'].str.contains("RTA", case=False, na=False)),
        ('TRPG', lambda d: d['tags'].str.contains("TRPG", case=False, na=False)),
        ('VTuber', lambda d: d['tags'].str.contains("VTuber", case=False, na=False)),
        ('歌ってみた', lambda d: d['tags'].str.contains("歌ってみた", case=False, na=False)),
        ('踊ってみた', lambda d: d['tags'].str.contains("踊ってみた", case=False, na=False)),
        ('ニコニコ技術部', lambda d: d['tags'].str.contains("ニコニコ技術部", case=False, na=False)),
        ('MMD', lambda d: d['tags'].str.contains("MMD", case=False, na=False)),
        ('音MAD', lambda d: d['tags'].str.contains("音MAD", case=False, na=False)),
        ('公式アニメ', lambda d: d['tags'].str.contains(r"dアニメストア|2025年.*アニメ", case=False, na=False)),
    ]

    # NOW: Removing priority, but applying specific exclusions as requested:
    # - RTA (純粋) excludes biim-system
    # - ゲーム（肉声・字幕等） = (contains game tags) AND (not Software Talk/Yukkuri)
    # - 音楽（その他） = (contains "音楽") AND (not matching ANY primary genre)
    
    # 1. First, define masks for each genre independently
    masks = {}
    for name, condition in priority_genres:
        masks[name] = condition(df)
    
    # 2. Apply specific exclusions
    # RTA (純粋) = RTA - biim
    masks['RTA（純粋）'] = masks['RTA（純粋）'] & ~masks['biim兄貴リスペクト OR biim兄貴']

    # Identify "any genre" mask (all initial genres)
    any_main_genre_mask = pd.Series(False, index=df.index)
    for name in masks:
        any_main_genre_mask |= masks[name]

    # Consolidated Game Genre: ゲーム（肉声・字幕等）
    # Logic: (Has game-related tags) AND (NOT Software Talk) AND (NOT Yukkuri)
    # Note: Includes "ゲーム実況", "実況プレイ動画", "プレイ動画", "ゲーム"
    game_tags_cond = df['tags'].str.contains(r"ゲーム|実況プレイ動画|プレイ動画", case=False, na=False)
    masks['ゲーム（肉声・字幕等）'] = game_tags_cond & ~masks['ソフトウェアトーク'] & ~masks['ゆっくり']
    
    # 音楽（その他） = (contains "音楽") & (not matching any main genre)
    music_cond = df['tags'].str.contains(r"(?:^| )音楽(?:$| )", regex=True, case=False, na=False)
    masks['音楽（その他）'] = music_cond & ~any_main_genre_mask

    # 3. Calculate results based on these refined masks
    genre_results = []
    display_order = [
        'ソフトウェアトーク', 'ゆっくり', 'VOCALOID', '公式アニメ', '例のアレ', 
        '音MAD', '歌ってみた', 'biim兄貴リスペクト OR biim兄貴', 'ゲーム（肉声・字幕等）',
        'MMD', '踊ってみた', 'VTuber', 'TRPG', 'RTA（純粋）', 'ニコニコ技術部', '音楽（その他）'
    ]
    for name in display_order:
        mask = masks[name]
        count = mask.sum()
        views = df.loc[mask, 'viewCounter'].sum()
        genre_results.append({
            'genre': name,
            'count': count,
            'views': views
        })
        print(f"Categorized {name:15}: {count:7,} videos")

    # Handle 'Others' (videos that don't match ANY of the above)
    any_genre_mask = pd.Series(False, index=df.index)
    for name in masks:
        any_genre_mask |= masks[name]

    others_mask = ~any_genre_mask
    genre_results.append({
        'genre': 'その他',
        'count': others_mask.sum(),
        'views': df.loc[others_mask, 'viewCounter'].sum()
    })
    print(f"Categorized {'その他':15}: {others_mask.sum():7,} videos")

    stats = pd.DataFrame(genre_results)

    # Calculate shares relative to TOTAL UNIQUE videos/views in this Top 30% set
    total_count = len(df)
    total_views = df['viewCounter'].sum()

    stats['count_share (%)'] = (stats['count'] / total_count * 100).round(2)
    stats['views_share (%)'] = (stats['views'] / total_views * 100).round(2)

    # Order the result: Sort by views_share (%) descending, but keep 'その他' at the bottom
    others_row = stats[stats['genre'] == 'その他']
    main_genres = stats[stats['genre'] != 'その他'].sort_values('views_share (%)', ascending=False)
    stats = pd.concat([main_genres, others_row])

    # Formatting for output
    print(f"\n--- 2025 NicoNico Genre Distribution (10000+ Views) ---")
    print(f"Threshold: {threshold:,} views")
    print(f"This threshold corresponds to Top {top_percentage:.2f}% of all videos.")
    print(f"Total Unique Videos (10000+): {total_count:,}")
    print(stats.to_markdown(index=False))

    # Save to file
    output_path = "results/genre_distribution_2025_10000plus.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# 2025年 ニコニコ動画 ジャンル別投稿数・再生数割合 (10000再生以上)\n\n")
        f.write(f"データ元: `results/all_2025.pickle` (2025年投稿動画)\n\n")
        f.write(f"再生数が10000回以上の動画のみを対象に集計しました。\n")
        f.write(f"10000再生は、全動画の中で上位 {top_percentage:.2f}% に相当します。\n\n")
        f.write("優先順位を排除し、重複を許可して集計しました。\n")
        f.write("- 「ゲーム（肉声・字幕等）」は、ゲーム関連タグを持つ動画から、ソフトウェアトーク・ゆっくりを除外したものです。\n")
        f.write("- 「RTA（純粋）」は、biim兄貴リスペクトを除外しています。\n")
        f.write("- 「音楽（その他）」は、主要ジャンルに該当しないが「音楽」タグを持つ動画です。\n\n")
        f.write(stats.to_markdown(index=False))
        f.write(f"\n\n- **再生数しきい値**: {threshold:,}回\n")
        f.write(f"- **上位パーセンタイル**: Top {top_percentage:.2f}%\n")
        f.write(f"- **対象動画数**: {total_count:,}\n")
        f.write(f"- **対象動画の総再生数**: {total_views:,}\n")

    print(f"\nResults saved to {output_path}")

    # Analyze top tags in 'Others'
    print(f"\n--- Top 100 Tags in 'Others' category (10000+ Views) ---")
    others_df = df[others_mask].copy()

    # 1. Get top tags by count
    all_others_tags_series = others_df['tags'].str.split(' ').explode()
    all_others_tags_series = all_others_tags_series[all_others_tags_series != ''].dropna()
    
    if len(all_others_tags_series) > 0:
        print("\nCalculating top tags by views...")
        top_500_tags_by_count = all_others_tags_series.value_counts().head(500).index.tolist()
        full_tag_stats = []
        for tag in top_500_tags_by_count:
            # Use non-capturing groups
            tag_mask = others_df['tags'].str.contains(f"(?:^| ){tag}(?:$| )", regex=True, case=False, na=False)
            full_tag_stats.append({
                'tag': tag,
                'count': tag_mask.sum(),
                'views': others_df.loc[tag_mask, 'viewCounter'].sum()
            })

        full_tag_stats_df = pd.DataFrame(full_tag_stats)
        full_tag_stats_df['count_share (%)'] = round(full_tag_stats_df['count'] / total_count * 100, 2)
        full_tag_stats_df['views_share (%)'] = round(full_tag_stats_df['views'] / total_views * 100, 2)

        tag_stats_count_sorted = full_tag_stats_df.sort_values('count', ascending=False).head(100)
        tag_stats_views_sorted = full_tag_stats_df.sort_values('views', ascending=False).head(100)

        # Save to files
        tags_count_output_path = 'results/others_top_tags_by_count_2025_10000plus.md'
        with open(tags_count_output_path, 'w', encoding='utf-8') as f:
            f.write("# 2025年 「その他」ジャンルにおける上位100タグ (投稿数順, 10000再生以上)\n\n")
            f.write(f"「その他」動画数: {others_mask.sum():,}\n")
            f.write(tag_stats_count_sorted.to_markdown(index=False))

        tags_views_output_path = 'results/others_top_tags_by_views_2025_10000plus.md'
        with open(tags_views_output_path, 'w', encoding='utf-8') as f:
            f.write("# 2025年 「その他」ジャンルにおける上位100タグ (再生数順, 10000再生以上)\n\n")
            f.write(f"「その他」動画数: {others_mask.sum():,}\n")
            f.write(tag_stats_views_sorted.to_markdown(index=False))

        print(f"\nTop 100 tags saved to {tags_count_output_path} and {tags_views_output_path}")

if __name__ == "__main__":
    analyze_genres()
