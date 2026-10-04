import shutil
from pathlib import Path

src_dir = Path(r"C:\Users\estshorter\src\nico-analyzer\results\poster_depth")
dst_dir = Path(r"C:\Users\estshorter\.gemini\antigravity-cli\brain\deac9e19-e720-414c-bc2d-ed5638311f62")

for img_file in src_dir.glob("*.png"):
    dst_file = dst_dir / img_file.name
    shutil.copy(img_file, dst_file)
    print(f"Copied {img_file.name} to artifacts directory.")
