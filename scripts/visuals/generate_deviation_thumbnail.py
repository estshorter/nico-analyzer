import matplotlib.pyplot as plt

def generate():
    # データ: 2018年の偏差値40 -> 2025年の偏差値55
    years = ['2018', '2025']
    values = [40, 55]
    
    # 配色: 黒背景に映えるネオンカラー
    # 2018年: 少し落ち着いたシアン / 2025年: 鮮やかなマゼンタ
    colors = ['#00E5FF', '#FF007F']

    # 16:9 の比率で作成 (背景透過)
    fig, ax = plt.subplots(figsize=(16, 9))
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    
    # 棒グラフの描画: サムネイルで見やすい太さに
    ax.bar(years, values, color=colors, width=0.6, zorder=3)

    # Y軸の範囲を調整（0基点にして、正確な比率を維持）
    ax.set_ylim(0, 60)

    # 全ての装飾を削除
    ax.axis('off')
    
    # 余白の調整（文字を入れるスペースを考慮し、上下左右に少しだけマージンを持たせる）
    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)

    # 保存
    output_path = "results/deviation_bar_chart.png"
    plt.savefig(output_path, dpi=300, transparent=True)
    print(f"Generated: {output_path}")

if __name__ == "__main__":
    generate()
