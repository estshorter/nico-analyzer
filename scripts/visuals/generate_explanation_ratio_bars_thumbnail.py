import matplotlib.pyplot as plt

def generate():
    # 2024年 解説ジャンル 再生時間別投稿数シェア
    labels = ['0-2m', '2-5m', '5-10m', '10-15m', '15m+']
    shares = [30.5, 20.1, 24.3, 13.4, 11.7]
    
    # 0-2mは強調色、他は目立ちにくい色
    colors = ['#00E5FF', '#222222', '#222222', '#222222', '#222222']

    fig, ax = plt.subplots(figsize=(16, 9))
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    
    # 棒グラフ
    bars = ax.bar(labels, shares, color=colors, width=0.7, zorder=3)

    # 30.5% という数字を目立たせる (オプションだが、ユーザーの意図を汲むなら)
    # ax.text(0, 31, '30.5%', color='#00E5FF', fontsize=40, ha='center', fontweight='bold')

    ax.set_ylim(0, 40)
    ax.axis('off')
    
    plt.subplots_adjust(left=0.1, right=0.9, top=0.8, bottom=0.1)

    output_path = "results/explanation_ratio_bars_thumbnail.png"
    plt.savefig(output_path, dpi=300, transparent=True)
    print(f"Generated: {output_path}")

if __name__ == "__main__":
    generate()
