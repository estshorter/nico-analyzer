import pickle
import pandas as pd

def load_data():
    with open('results/onboard.pickle', 'rb') as f:
        data = pickle.load(f)
    df = pd.DataFrame(data['data'])
    df['startTime'] = pd.to_datetime(df['startTime'])
    df['year'] = df['startTime'].dt.year
    return df

def analyze_part_distribution(df):
    results = []
    years = sorted([y for y in df['year'].unique() if 2015 <= y <= 2025])
    
    print("--- Analysis of 'Part' series concentration ---")
    
    for year in years:
        year_df = df[df['year'] == year]
        top_1000 = year_df.sort_values('viewCounter', ascending=False).head(1000)
        
        # Videos containing 'part' or 'Part'
        part_videos = top_1000[top_1000['title'].str.contains('part', case=False, na=False)]
        
        total_part_videos = len(part_videos)
        unique_users = part_videos['userId'].nunique()
        
        # Calculate how many videos the top 3 'part' posters account for
        if not part_videos.empty:
            user_counts = part_videos['userId'].value_counts()
            top_3_ratio = user_counts.head(3).sum() / total_part_videos
        else:
            top_3_ratio = 0
            
        results.append({
            'year': year,
            'part_video_count': total_part_videos,
            'unique_posters': unique_users,
            'avg_parts_per_user': total_part_videos / unique_users if unique_users > 0 else 0,
            'top_3_concentration': top_3_ratio
        })
    
    res_df = pd.DataFrame(results)
    print(res_df.to_string(index=False))

if __name__ == "__main__":
    df = load_data()
    analyze_part_distribution(df)
