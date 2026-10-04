import pickle
import pandas as pd
import os

def main():
    if not os.path.exists('results/onboard.pickle'):
        print("Error: results/onboard.pickle not found.")
        return

    with open('results/onboard.pickle', 'rb') as f:
        data = pickle.load(f)
    df = pd.DataFrame(data['data'])
    df['startTime'] = pd.to_datetime(df['startTime'])
    df['year'] = df['startTime'].dt.year
    
    # Filter years 2020-2025
    df = df[(df['year'] >= 2020) & (df['year'] <= 2025)]
    
    # Identify festival videos
    df['is_fest'] = df['tags'].str.contains("祭", na=False)
    
    results = []
    years = sorted(df['year'].unique())
    
    for year in years:
        year_df = df[df['year'] == year]
        
        # Overall stats
        total_videos = len(year_df)
        total_creators = year_df['userId'].nunique()
        avg_posts_per_creator = total_videos / total_creators if total_creators > 0 else 0
        
        # Festival stats
        fest_df = year_df[year_df['is_fest']]
        fest_videos = len(fest_df)
        fest_creators = fest_df['userId'].nunique()
        
        # Breakdown of creators by participation
        fest_creator_ids = set(fest_df['userId'])
        non_fest_creators = total_creators - len(fest_creator_ids)
        
        # Did fest creators post anything else?
        fest_creators_total_posts = year_df[year_df['userId'].isin(fest_creator_ids)]['userId'].value_counts()
        fest_creators_fest_posts = fest_df['userId'].value_counts()
        
        # Align indices before comparison and fill missing with 0
        aligned_total, aligned_fest = fest_creators_total_posts.align(fest_creators_fest_posts, fill_value=0)
        
        # Creators who ONLY posted in festivals
        only_fest_creators = sum(aligned_total == aligned_fest)
        
        results.append({
            'year': year,
            'total_videos': total_videos,
            'fest_videos': fest_videos,
            'fest_video_ratio': f"{(fest_videos/total_videos*100):.1f}%",
            'total_creators': total_creators,
            'fest_creators': fest_creators,
            'fest_creator_ratio': f"{(fest_creators/total_creators*100):.1f}%",
            'only_fest_creators': only_fest_creators,
            'avg_posts_overall': f"{avg_posts_per_creator:.2f}"
        })
        
    res_df = pd.DataFrame(results)
    print("--- 投稿祭の影響分析 (2020-2025) ---")
    print(res_df.to_string(index=False))

if __name__ == "__main__":
    main()
