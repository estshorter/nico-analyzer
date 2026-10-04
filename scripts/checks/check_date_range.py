import pandas as pd
import pickle
import os

def check_date_range():
    pickle_path = "results/all_2025.pickle"
    with open(pickle_path, "rb") as f:
        raw_data = pickle.load(f)
    df = pd.DataFrame(raw_data["data"])
    df["startTime"] = pd.to_datetime(df["startTime"])
    print(f"Min date: {df['startTime'].min()}")
    print(f"Max date: {df['startTime'].max()}")

if __name__ == "__main__":
    check_date_range()
