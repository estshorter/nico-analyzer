import matplotlib.pyplot as plt
import matplotlib as mpl

# Set font for Japanese text support
# Assuming a standard font like 'Meiryo' or 'MS Gothic' on Windows
mpl.rcParams['font.family'] = 'MS Gothic'

def generate_graph():
    # Data from results/genre_distribution_2025_refined.md (再生数)
    genres = ['例のアレ', 'VOCALOID', 'ボイロ']
    counts = [147353437, 182993427, 288697685]
    colors = ['#FF4D4D', '#FF4D4D', '#FFFFFF']

    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot horizontal bars
    bars = ax.barh(genres, counts, color=colors, height=0.6)

    # Remove all axis lines, labels, ticks, and grid
    ax.axis('off')
    ax.set_xticks([])
    ax.set_yticks([])

    # Set the target background color (though it will be transparent in the final save)
    fig.patch.set_facecolor('#0F172A')
    ax.set_facecolor('#0F172A')

    # Save as transparent PNG
    output_path = 'results/genre_comparison_top3_2025.png'
    plt.savefig(output_path, transparent=True, bbox_inches='tight', dpi=300)
    print(f"Graph saved to {output_path}")

if __name__ == "__main__":
    generate_graph()
