import matplotlib.pyplot as plt

def generate():
    # データ: 2024年の解説ジャンル
    # 0〜2分: 2504件
    # 2分超: 5715件
    labels = ['0-2min', '>2min']
    counts = [2504, 5715]
    
    # 配色: 0-2分は目立つシアン、それ以外は目立ちにくい非常に暗いグレー
    colors = ['#00E5FF', '#222222']

    # 16:9 の比率で作成 (黒背景)
    fig, ax = plt.subplots(figsize=(16, 9))
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    
    # 棒グラフの描画
    ax.bar(labels, counts, color=colors, width=0.6, zorder=3)

    # Y軸の範囲を調整
    ax.set_ylim(0, max(counts) * 1.1)

    # 全ての装飾を削除
    ax.axis('off')
    
    # 余白の調整
    plt.subplots_adjust(left=0.2, right=0.8, top=0.8, bottom=0.1)

    # 保存
    output_path = "results/explanation_short_thumbnail.png"
    plt.savefig(output_path, dpi=300, transparent=True)
    print(f"Generated: {output_path}")

if __name__ == "__main__":
    generate()
