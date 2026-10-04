import pandas as pd
from common_utils import filter_software_talk

# Load and filter data
raw_data = pd.read_pickle("results/software_talk.pickle")
df = pd.DataFrame(raw_data['data'])
df = filter_software_talk(df)

# Convert startTime to datetime
df['startTime'] = pd.to_datetime(df['startTime'])
df['year'] = df['startTime'].dt.year

max_date = df['startTime'].max()
print(f"Max date in dataset: {max_date}")

# Get first post date for each user
first_posts = df.groupby('userId')['startTime'].min().reset_index()
first_posts['first_year'] = first_posts['startTime'].dt.year

# 2022 completely new users
users_2022 = first_posts[first_posts['first_year'] == 2022]['userId'].unique()
print(f"Total completely new users in 2022: {len(users_2022)}")

# Filter df for only these users
df_2022_cohort = df[df['userId'].isin(users_2022)]

# See how many of them posted in each subsequent year
for year in sorted(df_2022_cohort['year'].unique()):
    if year >= 2022:
        active_users = df_2022_cohort[df_2022_cohort['year'] == year]['userId'].nunique()
        print(f"{year}: {active_users} ({(active_users/len(users_2022))*100:.1f}%)")

# What about "current" survival? 
# i.e., posted within the last 365 days of the max date in the dataset
one_year_ago = max_date - pd.Timedelta(days=365)
recent_active = df_2022_cohort[df_2022_cohort['startTime'] >= one_year_ago]['userId'].nunique()
print(f"Active in the last 365 days (since {one_year_ago.date()}): {recent_active} ({(recent_active/len(users_2022))*100:.1f}%)")
