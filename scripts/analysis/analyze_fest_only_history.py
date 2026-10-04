import pickle
import pandas as pd
import os

def main():
    if not os.path.exists('results/onboard.pickle'):
        print("Error: results/onboard.pickle not found.")
        return

    print("Loading data...")
    with open('results/onboard.pickle', 'rb') as f:
        data = pickle.load(f)
    df = pd.DataFrame(data['data'])
    df['startTime'] = pd.to_datetime(df['startTime'])
    df['year'] = df['startTime'].dt.year
    df['is_fest'] = df['tags'].str.contains("祭", na=False)
    
    # We will analyze the "Fest-only" creators for recent years (2023, 2024, 2025)
    target_years = [2023, 2024, 2025]
    results = []

    for target_year in target_years:
        year_df = df[df['year'] == target_year]
        
        # 1. Identify "Fest-only" creators in the target year
        total_posts_per_user = year_df['userId'].value_counts()
        fest_posts_per_user = year_df[year_df['is_fest']]['userId'].value_counts()
        
        aligned_total, aligned_fest = total_posts_per_user.align(fest_posts_per_user, fill_value=0)
        fest_only_user_ids = aligned_total[aligned_total == aligned_fest].index.tolist()
        
        # 2. Analyze their history BEFORE the target year
        newcomers = 0
        returning = 0
        burned_out = 0
        fest_veteran = 0
        
        for uid in fest_only_user_ids:
            # All posts by this user before target year
            past_posts = df[(df['userId'] == uid) & (df['year'] < target_year)]
            
            if past_posts.empty:
                newcomers += 1
            else:
                last_post_year = past_posts['year'].max()
                if last_post_year == target_year - 1:
                    # They posted last year. But did they post normal videos?
                    posts_last_year = past_posts[past_posts['year'] == last_post_year]
                    # Check if they had any non-festival posts last year
                    if not posts_last_year[~posts_last_year['is_fest']].empty:
                        burned_out += 1  # Transitioned from normal to fest-only
                    else:
                        fest_veteran += 1 # Was already fest-only last year
                else:
                    returning += 1
                    
        total_fest_only = len(fest_only_user_ids)
        results.append({
            'Year': target_year,
            'Total Fest-Only': total_fest_only,
            'Newcomers (新規)': f"{newcomers} ({newcomers/total_fest_only*100:.1f}%)",
            'Returning (復帰)': f"{returning} ({returning/total_fest_only*100:.1f}%)",
            'Burned-out (疲弊・移行)': f"{burned_out} ({burned_out/total_fest_only*100:.1f}%)",
            'Fest-Veteran (祭定着)': f"{fest_veteran} ({fest_veteran/total_fest_only*100:.1f}%)"
        })
        
    res_df = pd.DataFrame(results)
    print("\n--- 「祭専門」クリエイターの正体（より厳密な履歴分類） ---")
    print("Newcomers (新規): その年が初めての車載カテゴリ投稿")
    print("Returning (復帰): 過去に投稿があるが、前年は投稿していない")
    print("Burned-out (疲弊・移行): 前年は【通常動画】も投稿していたが、今年は【祭】だけになった人")
    print("Fest-Veteran (祭定着): 前年も今年も【祭】にしか投稿していない人\n")
    print(res_df.to_string(index=False))

if __name__ == "__main__":
    main()
