import sys
import pickle
import pandas as pd
import requests
import xml.etree.ElementTree as ET
import datetime
import time

def get_nickname(user_id):
    url = f'https://seiga.nicovideo.jp/api/user/info?id={user_id}'
    header = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=header)
        if r.status_code == 200:
            root = ET.fromstring(r.text)
            nickname = root.findtext("user/nickname")
            if nickname:
                return nickname
            else:
                return "Unknown (No nickname found)"
        else:
            return f"Error {r.status_code}"
    except Exception as e:
        return f"Error: {e}"

def main(category):
    pickle_path = f"results/{category}.pickle"
    try:
        with open(pickle_path, "rb") as f:
            recv = pickle.load(f)
    except FileNotFoundError:
        print(f"Error: File {pickle_path} not found.")
        return

    df = pd.json_normalize(recv["data"])
    df["startTime"] = pd.to_datetime(df["startTime"])
    df.fillna({"userId": 0}, inplace=True)
    df["userId"] = df["userId"].astype("uint64")
    
    df_valid = df[df["userId"] != 0]
    
    # Define active users: Last post within 1 year of the latest post in the dataset
    now = df_valid["startTime"].max()
    cutoff_date = now - pd.DateOffset(years=1)
    
    print(f"Dataset Latest Date: {now}")
    print(f"Active User Cutoff: {cutoff_date}")
    
    # Get last post date for each user
    user_max = df_valid.groupby("userId")["startTime"].max()
    
    # Filter for active users
    active_user_ids = user_max[user_max > cutoff_date].index
    print(f"Found {len(active_user_ids)} active users.")
    
    # Get debut date for active users
    # Filter original df for these users to get their min startTime
    df_active = df_valid[df_valid["userId"].isin(active_user_ids)]
    user_debut = df_active.groupby("userId")["startTime"].min()
    
    # Sort by debut date (ascending = oldest first)
    longest_active = user_debut.sort_values(ascending=True).head(50)
    
    print(f"\nTop 50 Longest Active Users (Category: {category})")
    print(f"{'Rank':<4} {'Debut Date':<12} {'UserID':<12} {'Nickname'}")
    print("-" * 60)
    
    for rank, (user_id, debut_date) in enumerate(longest_active.items(), 1):
        nickname = get_nickname(user_id)
        print(f"{rank:<4} {debut_date.strftime('%Y-%m-%d'):<12} {user_id:<12} {nickname}")
        time.sleep(0.2) # Rate limit protection

if __name__ == "__main__":
    if len(sys.argv) > 1:
        category = sys.argv[1]
    else:
        print("Usage: python get_longest_active_users.py <category>")
        print("Defaulting to 'travel'...")
        category = "travel"
    main(category)
