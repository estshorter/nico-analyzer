import time
import random
import sys
import os
import pickle
import ctypes
from pathlib import Path

# Windowsの仮想ターミナル処理 (VT) をより確実に有効化する
def enable_windows_vt():
    if os.name == 'nt':
        # kernel32からハンドルを取得してモードを設定
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11) # STD_OUTPUT_HANDLE
        mode = ctypes.c_uint()
        kernel32.GetConsoleMode(handle, ctypes.byref(mode))
        # ENABLE_VIRTUAL_TERMINAL_PROCESSING (0x0004) を追加
        kernel32.SetConsoleMode(handle, mode.value | 0x0004)

enable_windows_vt()

def progress_bar(iterable, prefix='', suffix='', decimals=1, length=50, fill='█', print_end="\r"):
    total = len(iterable)
    def print_progress(iteration):
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filled_length = int(length * iteration // total)
        bar = fill * filled_length + '-' * (length - filled_length)
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=print_end)
    
    print_progress(0)
    for i, item in enumerate(iterable):
        yield item
        print_progress(i + 1)
    print()

def simulate_analysis():
    pickle_dir = Path("results")
    genres = ["onboard", "travel", "kitchen", "explanation", "theater", "game", "software_talk"]
    # pickle_files = list(pickle_dir.glob("*.pickle"))
    pickle_files = [pickle_dir / (genre + ".pickle") for genre in genres]

    colors = {
        "cyan": "\033[36m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "red": "\033[31m",
        "white": "\033[37m",
        "magenta": "\033[35m",
        "end": "\033[0m",
        "bold": "\033[1m",
        "b_cyan": "\033[1;36m",
        "b_green": "\033[1;32m",
        "b_white": "\033[1;37m",
        "b_magenta": "\033[1;35m"
    }

    print(f"{colors['b_cyan']}>>> NICONICO VOICEROID CROSS-GENRE ANALYZER v3.5.0{colors['end']}")
    print(f"Targeting dataset: 2011-2025 (Local Pickle Files)\n")
    time.sleep(0.8)

    all_record_count = 0

    for pf in pickle_files:
        genre_name = pf.stem.upper()
        print(f"[PHASE] INGESTING GENRE: {colors['b_magenta']}{genre_name}{colors['end']}")

        
        # ロード中っぽく見せる
        for _ in progress_bar(range(30), prefix=f'  Loading {pf.name}', suffix='Memory Map', length=30):
            time.sleep(random.uniform(0.01, 0.03))
            
        try:
            with open(pf, "rb") as f:
                raw_data = pickle.load(f)
                data = raw_data.get("data", [])
                count = len(data)
                all_record_count += count
        except Exception as e:
            print(f"{colors['red']}  Error loading {pf.name}: {e}{colors['end']}")
            continue

        print(f"- Loaded {count:,} records.{colors['end']}")
        time.sleep(0.2)

        # 実際のデータを高速スキャン
        # print(f"{colors['yellow']}  Cross-referencing Metadata...{colors['end']}")
        # sample_size = min(60, count)
        # samples = random.sample(data, sample_size)
        
        # for item in samples:
        #     cid = item.get("contentId", "unknown")
        #     title = item.get("title", "")[:30] # 長すぎると崩れるのでカット
        #     views = item.get("viewCounter", 0)
        #     date = item.get("startTime", "")[:10]
            
        #     # ハイスピードログ出力
        #     sys.stdout.write(f"  SCAN: {cid} | {date} | V:{str(views):>8} | {title:<30} | OK\n")
        #     sys.stdout.flush()
        #     time.sleep(0.005) # 高速！

    # 3. 統合・計算フェーズ
    print(f"\n{colors['white']}STEP 3: Multi-Genre Statistical Synthesis...{colors['end']}")
    
    tasks = [
        ("Survival Curve Fitting (Kaplan-Meier)", 0.02),
        ("Cross-Genre Correlation Matrix", 0.03),
        ("Active User Ratio Calculation", 0.015),
        ("Market Share Share Distribution", 0.04),
        ("Final Graph Rendering (300 DPI)", 0.02)
    ]

    for task, speed in tasks:
        for _ in progress_bar(range(20), prefix=f'  CALC: {task:<40}', suffix='Done', length=20):
            time.sleep(random.uniform(speed*0.5, speed*1.5))

    print(f"\n{colors['bold']}{colors['green']}ALL ANALYSES COMPLETED SUCCESSFULLY.{colors['end']}")
    print(f"Final outputs generated in results/comparison/")
    print(f"Total entries processed: {all_record_count:,} records")
if __name__ == "__main__":
    simulate_analysis()
