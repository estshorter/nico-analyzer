# /// script
# dependencies = [
#   "html2image",
#   "pandas",
#   "numpy",
#   "jinja2",
# ]
# ///

import pickle
from pathlib import Path
import pandas as pd
import numpy as np
from jinja2 import Template
from html2image import Html2Image

from common_utils import filter_software_talk

def preprocess(category):
    pickle_path = Path(f"results/{category}.pickle")
    if not pickle_path.exists():
        return None
    with open(pickle_path, "rb") as f:
        recv = pickle.load(f)
    df = pd.json_normalize(recv["data"])
    if category == "software_talk":
        df = filter_software_talk(df)
    df["startTime"] = pd.to_datetime(df["startTime"])
    df["year"] = df["startTime"].dt.year
    df["viewCounter"] = df["viewCounter"].astype(float)
    return df

def get_stats(category):
    df = preprocess(category)
    if df is None: return None
    data_2025 = df[df["year"] == 2025]["viewCounter"].values
    if len(data_2025) == 0: return None
    median = np.median(data_2025)
    top30_threshold = np.percentile(data_2025, 70)
    return int(median), int(top30_threshold)

# Tailwind CSS を使用した改良版テンプレート (直角・シャープ・ダークモード)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', 'Noto Sans JP', sans-serif; }
        .glass { background: rgba(10, 15, 30, 0.9); backdrop-filter: blur(16px); }
        .neon-blue { text-shadow: 0 0 15px rgba(55, 148, 255, 0.6); }
        .neon-orange { text-shadow: 0 0 15px rgba(255, 159, 67, 0.6); }
        /* 直角のエッジを強調するための追加ボーダー */
        .edge-glow { border: 1px solid rgba(255, 255, 255, 0.1); }
    </style>
</head>
<body class="bg-slate-950 p-12 flex items-center justify-center min-h-screen">
    <div class="glass rounded-none shadow-[0_0_60px_rgba(0,0,0,0.9)] overflow-hidden inline-block border border-slate-700">
        <table class="text-left border-collapse">
            <thead>
                <tr class="bg-slate-900 border-b-2 border-slate-700">
                    {% for col in col_labels %}
                    <th class="px-14 py-10 text-white text-3xl font-black uppercase tracking-[0.2em] text-center border-x border-slate-700/50 first:border-l-0 last:border-r-0">{{ col }}</th>
                    {% endfor %}
                </tr>
            </thead>
            <tbody class="divide-y divide-slate-800">
                {% for row in data %}
                <tr class="hover:bg-slate-800/50 transition-colors">
                    <td class="px-14 py-9 border-x border-slate-800 first:border-l-0">
                        <div class="text-slate-100 font-bold text-3xl tracking-tight">{{ row[0] }}</div>
                    </td>
                    <td class="px-14 py-9 text-center border-x border-slate-800">
                        <span class="text-6xl font-black text-blue-400 neon-blue">
                            {{ row[1] }}
                        </span>
                        <span class="text-slate-500 text-xl font-bold ml-3 italic uppercase">Views</span>
                    </td>
                    {% if row|length > 2 %}
                    <td class="px-14 py-9 text-center border-x border-slate-800 last:border-r-0">
                        <span class="text-6xl font-black text-orange-400 neon-orange">
                            {{ row[2] }}
                        </span>
                        <span class="text-slate-500 text-xl font-bold ml-3 italic uppercase">Views</span>
                    </td>
                    {% endif %}
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</body>
</html>
"""

def generate_cool_tables():
    hti = Html2Image(output_path='results', custom_flags=['--no-sandbox', '--disable-gpu'])
    template = Template(HTML_TEMPLATE)
    
    # 1. 車載動画目標
    onboard_stats = get_stats("onboard")
    if onboard_stats:
        data = [
            ["第一目標 (中央値)", f"{onboard_stats[0]:,}"],
            ["第二目標 (上位30%)", f"{onboard_stats[1]:,}"]
        ]
        html_content = template.render(data=data, col_labels=["目標段階", "目安再生数"])
        
        with open("results/table_onboard_tailwind.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        hti.screenshot(html_str=html_content, save_as="table_onboard_tailwind.png", size=(1200, 500))

    # 2. 全ジャンル目標 (ジャンル名を統一)
    genre_order = [
        ("onboard", "車載"),
        ("game", "実況"),
        ("theater", "劇場"),
        ("explanation", "解説"),
        ("kitchen", "キッチン"),
        ("travel", "旅行")
    ]
    all_genre_data = []
    for cat, name in genre_order:
        stats = get_stats(cat)
        if stats:
            all_genre_data.append([name, f"{stats[0]:,}", f"{stats[1]:,}"])
            
    html_content = template.render(data=all_genre_data, col_labels=["ジャンル", "第一目標 (中央値)", "第二目標 (上位30%)"])
    
    with open("results/table_all_genres_tailwind.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    hti.screenshot(html_str=html_content, save_as="table_all_genres_tailwind.png", size=(1600, 1000))
    print("Generated Updated Tailwind Tables with consistent genre names in results/")

if __name__ == "__main__":
    generate_cool_tables()
