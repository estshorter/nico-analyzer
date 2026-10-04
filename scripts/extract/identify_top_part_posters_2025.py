import pickle
import pandas as pd

def load_data():
    with open('results/onboard.pickle', 'rb') as f:
        data = pickle.load(f)
    df = pd.DataFrame(data['data'])
    df['startTime'] = pd.to_datetime(df['startTime'])
    df['year'] = df['startTime'].dt.year
    return df

def identify_top_3(df, year=2025):
    print(f"--- Identifying Top 3 'Part' Posters in {year} ---")
    
    year_df = df[df['year'] == year]
    # Top 1000 by viewCounter
    top_1000 = year_df.sort_values('viewCounter', ascending=False).head(1000)
    
    # Filter 'Part' videos
    part_videos = top_1000[top_1000['title'].str.contains('part', case=False, na=False)].copy()
    
    if part_videos.empty:
        print("No 'Part' videos found in the top 1000.")
        return

    # Count by userId
    user_counts = part_videos['userId'].value_counts()
    top_3_ids = user_counts.head(3).index.tolist()
    
    for i, user_id in enumerate(top_3_ids, 1):
        count = user_counts[user_id]
        # Get sample titles for identification
        sample_titles = part_videos[part_videos['userId'] == user_id]['title'].head(3).tolist()
        print(f"\nRank {i}: User ID {user_id}")
        print(f"Video Count in Top 1000: {count}")
        print(f"Sample Titles:")
        for title in sample_titles:
            print(f"  - {title}")

if __name__ == "__main__":
    df = load_data()
    identify_top_3(df)
