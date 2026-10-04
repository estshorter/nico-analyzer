import pickle
import pandas as pd
from pathlib import Path

def check_structure(genre):
    input_path = Path(f"results/{genre}.pickle")
    if not input_path.exists():
        print(f"File not found: {input_path}")
        return

    with open(input_path, "rb") as f:
        data = pickle.load(f)
    
    print(f"Genre: {genre}")
    print(f"Type: {type(data)}")
    if isinstance(data, dict):
        print(f"Dict Keys: {data.keys()}")
        if "data" in data:
            print(f"data type: {type(data['data'])}")
            if isinstance(data["data"], list) and len(data["data"]) > 0:
                print(f"data[0] type: {type(data['data'][0])}")
                if isinstance(data["data"][0], dict):
                    print(f"data[0] keys: {data['data'][0].keys()}")
    elif isinstance(data, list) and len(data) > 0:
        print(f"First element type: {type(data[0])}")
        if isinstance(data[0], dict):
            print(f"Keys: {data[0].keys()}")
    elif isinstance(data, pd.DataFrame):
        print(f"Columns: {data.columns}")
    print("-" * 20)

def main():
    genres = ["onboard", "travel", "kitchen", "explanation", "theater"]
    for genre in genres:
        check_structure(genre)

if __name__ == "__main__":
    main()
