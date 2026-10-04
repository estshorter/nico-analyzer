import os

html_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', 'Noto Sans JP', sans-serif; background: #020617; color: white; }
        .glass { background: rgba(40, 53, 75, 0.8); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.25); }
        
        .bucket-fill {
            background: linear-gradient(to top, rgba(255, 79, 129, 0.4) 40%, transparent 40%);
        }
    </style>
</head>
<body class="flex flex-col items-center min-h-screen justify-center overflow-hidden">
    
    <div class="relative flex-shrink-0" style="width: 1000px; height: 750px;">
        
        <!-- 背景のフロー線 (SVG) -->
        <svg class="absolute inset-0 w-full h-full" style="z-index: 0;">
            <defs>
                <linearGradient id="flowGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" style="stop-color:#ff4f81;stop-opacity:0.8" />
                    <stop offset="100%" style="stop-color:#4facfe;stop-opacity:0.8" />
                </linearGradient>
            </defs>
            <g stroke="url(#flowGrad)" stroke-width="8" fill="none" stroke-linecap="round" stroke-linejoin="round" class="opacity-80">
                <!-- TOP to MID A -->
                <path d="M 500 160 C 500 220, 300 200, 300 260" />
                <!-- TOP to MID B -->
                <path d="M 500 160 C 500 220, 700 200, 700 260" />
                
                <!-- MID A to NEWBIE 1 -->
                <path d="M 300 380 C 300 440, 200 420, 200 480" />
                <!-- MID A to NEWBIE 2 -->
                <path d="M 300 380 C 300 440, 400 420, 400 480" />
                
                <!-- MID B to NEWBIE 3 -->
                <path d="M 700 380 C 700 440, 600 420, 600 480" />
                <!-- MID B to NEWBIE 4 -->
                <path d="M 700 380 C 700 440, 800 420, 800 480" />
            </g>
        </svg>

        <!-- TOP TIER -->
        <div class="absolute glass rounded-t-xl rounded-b-3xl flex flex-col items-center justify-center overflow-hidden bucket-fill z-10" 
             style="top: 40px; left: 300px; width: 400px; height: 120px; box-shadow: 0 0 30px rgba(255,79,129,0.3);">
            <span class="text-sm font-bold text-slate-300 uppercase tracking-widest">Top Tier</span>
            <span class="text-3xl font-black">人気投稿者の動画</span>
        </div>

        <!-- MID TIER A -->
        <div class="absolute glass rounded-t-lg rounded-b-2xl flex flex-col items-center justify-center overflow-hidden bucket-fill z-10"
             style="top: 260px; left: 160px; width: 280px; height: 120px; box-shadow: 0 0 20px rgba(79,172,254,0.2);">
            <span class="text-sm font-bold text-slate-300 uppercase">Mid Tier</span>
            <span class="text-2xl font-bold">中堅動画 A</span>
        </div>
        
        <!-- MID TIER B -->
        <div class="absolute glass rounded-t-lg rounded-b-2xl flex flex-col items-center justify-center overflow-hidden bucket-fill z-10"
             style="top: 260px; left: 560px; width: 280px; height: 120px; box-shadow: 0 0 20px rgba(79,172,254,0.2);">
            <span class="text-sm font-bold text-slate-300 uppercase">Mid Tier</span>
            <span class="text-2xl font-bold">中堅動画 B</span>
        </div>

        <!-- NEWBIE 1 -->
        <div class="absolute glass rounded-t-md rounded-b-xl flex flex-col items-center justify-center bucket-fill z-10"
             style="top: 480px; left: 110px; width: 180px; height: 90px; box-shadow: 0 0 15px rgba(79,172,254,0.15);">
            <span class="text-sky-400 font-bold text-xl">新人動画 1</span>
        </div>
        <!-- NEWBIE 2 -->
        <div class="absolute glass rounded-t-md rounded-b-xl flex flex-col items-center justify-center bucket-fill z-10"
             style="top: 480px; left: 310px; width: 180px; height: 90px; box-shadow: 0 0 15px rgba(79,172,254,0.15);">
            <span class="text-sky-400 font-bold text-xl">新人動画 2</span>
        </div>
        <!-- NEWBIE 3 -->
        <div class="absolute glass rounded-t-md rounded-b-xl flex flex-col items-center justify-center bucket-fill z-10"
             style="top: 480px; left: 510px; width: 180px; height: 90px; box-shadow: 0 0 15px rgba(79,172,254,0.15);">
            <span class="text-sky-400 font-bold text-xl">新人動画 3</span>
        </div>
        <!-- NEWBIE 4 -->
        <div class="absolute glass rounded-t-md rounded-b-xl flex flex-col items-center justify-center bucket-fill z-10"
             style="top: 480px; left: 710px; width: 180px; height: 90px; box-shadow: 0 0 15px rgba(79,172,254,0.15);">
            <span class="text-sky-400 font-bold text-xl">新人動画 4</span>
        </div>

    </div>
</body>
</html>
"""

output_path = "results/visualization_cascade_flow.html"
os.makedirs("results", exist_ok=True)
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"トリクルダウン視覚化HTMLを更新しました: {output_path}")
