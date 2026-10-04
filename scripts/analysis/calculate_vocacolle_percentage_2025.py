import pandas as pd
import pickle
import os

def analyze_vocacolle_percentage():
    pickle_path = "results/all_2025.pickle"
    if not os.path.exists(pickle_path):
        print(f"Error: {pickle_path} not found.")
        return

    print(f"Loading {pickle_path}...")
    with open(pickle_path, "rb") as f:
        raw_data = pickle.load(f)

    df = pd.DataFrame(raw_data["data"])
    df["startTime"] = pd.to_datetime(df["startTime"])
    
    # VOCALOID classification logic from analyze_all_genres_distribution_2025_refined.py
    df["tags"] = df["tags"].fillna("").astype(str)
    vocaloid_include = "VOCALOID|ボカロ|初音ミク|UTAU|Synthesizer_V|SynthesizerV|ボカコレ|VoiSona|NEUTRINO|VOICEPEAKオリジナル曲"
    cevio_music_limit = "VOCALOID|VOCAROID|音楽|歌うボイスロイド|CeVIOカバー曲|CeVIOオリジナル曲|歌ってみた"
    
    vocaloid_mask = df['tags'].str.contains(vocaloid_include, case=False, na=False) | \
                    (df['tags'].str.contains("CeVIO", case=False, na=False) & \
                     df['tags'].str.contains(cevio_music_limit, case=False, na=False))
    
    df_vocaloid = df[vocaloid_mask].copy()
    total_vocaloid = len(df_vocaloid)
    print(f"Total VOCALOID videos in 2025: {total_vocaloid:,}")

    # Define periods
    # Winter: 2/21-2/24
    # Summer: 8/21-8/25
    winter_start = pd.Timestamp("2025-02-21 00:00:00+09:00")
    winter_end = pd.Timestamp("2025-02-24 23:59:59+09:00")
    summer_start = pd.Timestamp("2025-08-21 00:00:00+09:00")
    summer_end = pd.Timestamp("2025-08-25 23:59:59+09:00")

    # Filter by period
    winter_mask = (df_vocaloid["startTime"] >= winter_start) & (df_vocaloid["startTime"] <= winter_end)
    summer_mask = (df_vocaloid["startTime"] >= summer_start) & (df_vocaloid["startTime"] <= summer_end)
    combined_mask = winter_mask | summer_mask

    winter_count = winter_mask.sum()
    summer_count = summer_mask.sum()
    combined_count = combined_mask.sum()

    print("\nResults for VOCALOID:")
    print(f"Winter (2/21-2/24): {winter_count:,} videos ({winter_count/total_vocaloid*100:.2f}%)")
    print(f"Summer (8/21-8/25): {summer_count:,} videos ({summer_count/total_vocaloid*100:.2f}%)")
    print(f"Combined (Winter + Summer): {combined_count:,} videos ({combined_count/total_vocaloid*100:.2f}%)")

if __name__ == "__main__":
    analyze_vocacolle_percentage()
