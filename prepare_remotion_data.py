import json
from pathlib import Path

def generate_remotion_data():
    print("Extracting data for Remotion...")
    
    md_path = Path("results/top_20_2025_comparison.md")
    
    genres_data = {
        "overall": [],
        "game": [],
        "theater": [],
        "explanation": [],
        "kitchen": [],
        "onboard": [],
        "travel": []
    }
    
    if md_path.exists():
        with open(md_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        start_parsing = False
        for line in lines:
            if "|    1 |" in line or "| 1 |" in line:
                start_parsing = True
            if start_parsing and "|" in line:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 8:
                    def extract_name(text):
                        if not text: return ""
                        return text.split("(")[0].strip()
                    
                    genres_data["overall"].append(extract_name(parts[2]))
                    genres_data["game"].append(extract_name(parts[3]))
                    genres_data["theater"].append(extract_name(parts[4]))
                    genres_data["explanation"].append(extract_name(parts[5]))
                    genres_data["kitchen"].append(extract_name(parts[6]))
                    genres_data["onboard"].append(extract_name(parts[7]))
                    genres_data["travel"].append(extract_name(parts[8]))
                    
                if "|   20 |" in line or "| 20 |" in line:
                    break
    else:
        print(f"File not found: {md_path}")
        return

    # TOP10に1度でも登場した全キャラクターをリストアップ
    top10_chars = set()
    for genre, ranks_list in genres_data.items():
        top10_chars.update(ranks_list[:10])
    
    if "" in top10_chars:
        top10_chars.remove("")

    # 各キャラクターの色やアイコンの定義
    char_info_map = {
        "結月ゆかり": {"id": "yukari", "color": "#DA70D6", "icon": "結月ゆかり.png"}, # オーキッド（明るい紫）
        "琴葉茜": {"id": "akane", "color": "#FF7F50", "icon": "琴葉茜.png"},
        "琴葉葵": {"id": "aoi", "color": "#6495ED", "icon": "琴葉葵.png"},
        "紲星あかり": {"id": "akari", "color": "#FFA500", "icon": "紲星あかり.png"},
        "東北きりたん": {"id": "kiritan", "color": "#F4A460", "icon": "東北きりたん.png"}, # サンディブラウン（明るい茶色）
        "ずんだもん": {"id": "zundamon", "color": "#3CB371", "icon": "ずんだもん.png"},
        "春日部つむぎ": {"id": "tsumugi", "color": "#FFD700", "icon": "春日部つむぎ.png"},
        "弦巻マキ": {"id": "maki", "color": "#FF4500", "icon": "弦巻マキ.png"},
        "四国めたん": {"id": "metan", "color": "#FF69B4", "icon": "四国めたん.png"},
        "小春六花": {"id": "rikka", "color": "#6f93a0", "icon": "小春六花.png"},
        "夏色花梨": {"id": "karin", "color": "#97217f", "icon": "夏色花梨.png"},
        "花隈千冬": {"id": "chifuyu", "color": "#98FB98", "icon": "花熊千冬.png"},
        "東北ずん子": {"id": "zunko", "color": "#98FB98", "icon": "東北ずん子.png"},
        "東北イタコ": {"id": "itako", "color": "#57d5ec", "icon": "東北イタコ.png"}, # 明るいパープル
        "宮舞モカ": {"id": "moka", "color": "#4682B4", "icon": "宮舞モカ.png"},
        "冥鳴ひまり": {"id": "himari", "color": "#9370DB", "icon": "冥鳴ひまり.png"},
        "双葉湊音": {"id": "minato", "color": "#0071f2", "icon": "双葉湊音.png"}, # シアン/アクア
        "WhiteCUL": {"id": "whitecul", "color": "#3ab7ff", "icon": "WhiteCUL.png"}, # ホワイト
        "重音テト": {"id": "teto", "color": "#FF6347", "icon": "重音テト.png"},
        "すずきつづみ": {"id": "tsudumi", "color": "#4169E1", "icon": "すずきつづみ.png"},
        "さとうささら": {"id": "sasara", "color": "#FFB6C1", "icon": "さとうささら.png"},
        "音街ウナ": {"id": "una", "color": "#000080", "icon": "音街ウナ.png"},
        "もち子さん": {"id": "mochiko", "color": "#909090", "icon": "もち子さん.png"}, # グレー
    }

    # 順位データ構築
    characters = []
    for char_name in top10_chars:
        ranks = {}
        for genre in genres_data.keys():
            if char_name in genres_data[genre]:
                rank = genres_data[genre].index(char_name) + 1
            else:
                rank = 11 # 圏外は11とする
            ranks[genre] = rank
            
        info = char_info_map.get(char_name, {"id": char_name, "color": "#888888", "icon": f"{char_name}.png"})
        
        characters.append({
            "id": info["id"],
            "name": char_name,
            "icon": f"/icons/{info['icon']}",
            "color": info["color"],
            "ranks": ranks
        })
        
    # Sort characters by overall rank to keep the output stable
    characters.sort(key=lambda c: c["ranks"].get("overall", 100))

    remotion_data = {
        "characters": characters,
        "genres": list(genres_data.keys())
    }
    
    out_dir = Path("remotion-intro/src/data")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "ranks.json"
    
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(remotion_data, f, ensure_ascii=False, indent=2)
        
    print(f"Data saved to {out_file}")

if __name__ == "__main__":
    generate_remotion_data()
