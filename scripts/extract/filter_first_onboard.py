import argparse
import pandas as pd
import pickle

def parse_args():
    parser = argparse.ArgumentParser(description="Filter first onboard users active in the recent 1 year.")
    parser.add_argument("year", nargs="?", default=None, help="Target year (e.g. 2025) or 'all'")
    parser.add_argument("--year", "-y", dest="opt_year", default=None, help="Target year (e.g. 2025) or 'all'")
    parser.add_argument("--all", "-a", action="store_true", help="Filter all years")
    parser.add_argument("--pickle", "-p", default="results/onboard.pickle", help="Path to onboard pickle file")
    args = parser.parse_args()
    
    if args.all:
        target_year = "all"
    elif args.opt_year is not None:
        target_year = str(args.opt_year).lower()
    elif args.year is not None:
        target_year = str(args.year).lower()
    else:
        target_year = "all"

    if target_year != "all":
        try:
            target_year = int(target_year)
        except ValueError:
            target_year = "all"
            
    return target_year, args.pickle

def main():
    target_year, pickle_path = parse_args()

    # Load onboard.pickle
    print(f"Loading {pickle_path}...")
    with open(pickle_path, "rb") as f:
        data = pickle.load(f)
    
    # Convert list of dicts to DataFrame
    df_onboard = pd.DataFrame(data['data'])
    
    # Ensure userId is Int64 and startTime is datetime in JST
    df_onboard['userId'] = pd.to_numeric(df_onboard['userId'], errors='coerce').astype('Int64')
    df_onboard['startTime'] = pd.to_datetime(df_onboard['startTime'], utc=True).dt.tz_convert('Asia/Tokyo')
        
    latest_time = df_onboard['startTime'].max()
    print(f"Latest video time in {pickle_path}: {latest_time}")
    
    # Calculate threshold (1 year before)
    one_year_ago = latest_time - pd.DateOffset(years=1)
    print(f"Threshold for recent 1 year: {one_year_ago}")
    
    # Filter videos
    recent_videos = df_onboard[df_onboard['startTime'] >= one_year_ago]
    
    # Extract userIds
    recent_users = set(recent_videos['userId'].dropna().unique())
    print(f"Number of distinct users who posted in the last 1 year: {len(recent_users)}")
    
    # Load input CSV
    if target_year == "all":
        input_csv = "results/first_onboard_all.csv"
        output_path = "results/first_onboard_all_active_recent_1year.csv"
    else:
        input_csv = f"results/first_onboard_{target_year}.csv"
        output_path = f"results/first_onboard_{target_year}_active_recent_1year.csv"

    print(f"Loading {input_csv}...")
    df_first = pd.read_csv(input_csv)
    
    # Filter to only those in recent_users
    df_filtered = df_first[df_first['userId'].isin(recent_users)]
    
    print(f"Number of rows in {input_csv}: {len(df_first)}")
    print(f"Number of rows after filtering: {len(df_filtered)}")
    
    df_filtered.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"Saved extracted CSV to {output_path}")

    json_output_path = output_path.replace('.csv', '.json')
    df_filtered.to_json(json_output_path, orient='records', force_ascii=False, indent=2)
    print(f"Saved extracted JSON to {json_output_path}")

if __name__ == "__main__":
    main()
