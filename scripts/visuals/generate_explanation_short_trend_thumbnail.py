import matplotlib.pyplot as plt

def generate():
    # 2020年〜2024年の解説ジャンル 0〜2分動画の投稿数
    years = ['2020', '2021', '2022', '2023', '2024']
    counts = [552, 823, 1672, 2501, 2504]
    
    # 全ての年を同じ強調色（シアン）に設定
    colors = ['#00E5FF'] * len(years)

    fig, ax = plt.subplots(figsize=(16, 9))
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    
    # 棒グラフ
    ax.bar(years, counts, color=colors, width=0.6, zorder=3)

    # Y軸の範囲を調整
    ax.set_ylim(0, max(counts) * 1.2)

    # 装飾を削除
    ax.axis('off')
    
    # 余白の調整
    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)

    # 保存
    output_path = "results/explanation_short_trend_thumbnail.png"
    plt.savefig(output_path, dpi=300, transparent=True)
    print(f"Generated: {output_path}")

if __name__ == "__main__":
    generate()
