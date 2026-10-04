import pickle
import pandas as pd
from pathlib import Path
from common_utils import filter_software_talk

pickle_path = Path(r"results\software_talk.pickle")
print(f"Loading {pickle_path}...")
with open(pickle_path, "rb") as f:
    recv = pickle.load(f)

df = pd.json_normalize(recv["data"])
print(f"Original shape: {df.shape}")

df = filter_software_talk(df)
print(f"After filter shape: {df.shape}")

df["startTime"] = pd.to_datetime(df["startTime"])
print(f"Columns: {list(df.columns)}")
print(f"Min startTime: {df['startTime'].min()}, Max startTime: {df['startTime'].max()}")
print(f"Unique users: {df['userId'].nunique()}")
print(df.head(2))
