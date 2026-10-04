import json
import matplotlib.pyplot as plt
from pathlib import Path

def generate_slope_chart():
    # データの読み込み
    data_path = Path("remotion-intro/src/data/ranks.json")
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    characters = data["characters"]
    
    # 小樽組のID
    otaru_ids = ["rikka", "chifuyu", "karin"]
    
    # フィギュアの設定 (16:9, サムネイルサイズ 1280x720 相当)
    # dpi=100 なら 12.8x7.2
    fig, ax = plt.subplots(figsize=(16, 9), facecolor='white')
    ax.set_facecolor('white')

    # 小樽組の正確な順位データ (2025年集計に基づく)
    otaru_stats = {
        "rikka": {"overall": 10, "onboard": 3},
        "karin": {"overall": 18, "onboard": 10},
        "chifuyu": {"overall": 23, "onboard": 9}
    }

    # 各キャラクターの線を描画
    for char in characters:
        char_id = char["id"]
        is_otaru = char_id in otaru_ids
        
        # 順位データの取得
        ranks = char["ranks"]
        overall_rank = ranks.get("overall", 30)
        onboard_rank = ranks.get("onboard", 21)
        
        if is_otaru:
            # 小樽組は正確な順位を使用し、圧倒的に太く描画
            stats = otaru_stats[char_id]
            y = [stats["overall"], stats["onboard"]]
            color = char["color"]
            linewidth = 36
            alpha = 1.0
            zorder = 10
            ax.plot([0, 1], y, color=color, linewidth=linewidth, alpha=alpha, zorder=zorder, solid_capstyle='round')
        elif overall_rank <= 10 or onboard_rank <= 10:
            # その他は、どちらかでTOP10に入っているキャラのみを背景として描画
            # 視認性を保つため、過度な減衰（細さ・透明度）を避ける
            y = [overall_rank, onboard_rank]
            color = "#D0D0D0" 
            linewidth = 4
            alpha = 0.3
            zorder = 1
            ax.plot([0, 1], y, color=color, linewidth=linewidth, alpha=alpha, zorder=zorder, solid_capstyle='round')

    # 順位なのでY軸の設定（1位を上、20位を下にする）
    ax.set_ylim(20.5, 0.5)
    
    # X軸の左右に少し余白
    ax.set_xlim(-0.05, 1.05)

    # 全ての装飾を削除（軸、枠線、目盛り）
    ax.axis('off')
    
    # 余白をなくす
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

    # 保存
    output_path = "slope_chart_thumbnail.png"
    plt.savefig(output_path, dpi=120, facecolor='white', bbox_inches='tight', pad_inches=0)
    print(f"Slope chart generated: {output_path}")

if __name__ == "__main__":
    generate_slope_chart()
