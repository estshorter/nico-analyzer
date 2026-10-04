import os

html_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', 'Noto Sans JP', sans-serif; overflow: hidden; }
        .glass { background: rgba(10, 15, 30, 0.85); backdrop-filter: blur(12px); }
        /* アニメーションなしの静止スタイル */
        .neon-rose { box-shadow: 0 0 30px rgba(255, 79, 129, 0.4); border: 2px solid rgba(255, 79, 129, 0.6); }
        .neon-blue { box-shadow: 0 0 20px rgba(79, 172, 254, 0.3); border: 2px solid rgba(79, 172, 254, 0.5); }
        .flow-line {
            stroke-dasharray: none;
            opacity: 0.6;
        }
    </style>
</head>
<body class="bg-slate-950 flex items-center justify-center min-h-screen">
    
    <div class="relative w-[1000px] h-[700px]">
        <!-- 背景のタイトル -->
        <div class="absolute top-0 left-0 w-full text-center">
            <h1 class="text-slate-500 text-3xl font-black tracking-[0.3em] uppercase opacity-50">
                Synergy & Circulation Flow
            </h1>
            <p class="text-rose-400 text-5xl font-black mt-4 neon-rose inline-block px-8 py-2 bg-slate-900/80">
                キッチン界隈の「最強の回遊性」
            </p>
        </div>

        <!-- SVG 接続線 -->
        <svg class="absolute inset-0 w-full h-full" style="z-index: 0;">
            <defs>
                <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#ff4f81;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#4facfe;stop-opacity:1" />
                </linearGradient>
            </defs>
            
            <!-- 中心から各ノードへの線 -->
            <g stroke="url(#grad1)" stroke-width="4" fill="none">
                <line x1="500" y1="380" x2="200" y2="250" class="flow-line" />
                <line x1="500" y1="380" x2="800" y2="250" class="flow-line" />
                <line x1="500" y1="380" x2="150" y2="500" class="flow-line" />
                <line x1="500" y1="380" x2="850" y2="500" class="flow-line" />
                <line x1="500" y1="380" x2="500" y2="600" class="flow-line" />
                <line x1="500" y1="380" x2="350" y2="180" class="flow-line" />
                <line x1="500" y1="380" x2="650" y2="180" class="flow-line" />
            </g>
        </svg>

        <!-- 中心：トップ層 -->
        <div class="absolute top-[320px] left-[380px] w-[240px] h-[120px] glass neon-rose rounded-xl flex flex-col items-center justify-center z-10">
            <span class="text-rose-400 font-black text-xl mb-1">TOP TIER</span>
            <span class="text-white font-black text-3xl tracking-tighter">人気投稿者</span>
            <span class="text-rose-500 font-bold text-lg mt-1">動画時間：4分</span>
        </div>

        <!-- 周辺：中堅・新人 -->
        <div class="absolute top-[180px] left-[100px] w-[180px] py-4 glass neon-blue rounded-lg text-center">
            <span class="text-slate-400 text-sm font-bold block">MID TIER</span>
            <span class="text-white font-black text-xl">中堅投稿者 A</span>
        </div>
        <div class="absolute top-[180px] right-[100px] w-[180px] py-4 glass neon-blue rounded-lg text-center">
            <span class="text-slate-400 text-sm font-bold block">MID TIER</span>
            <span class="text-white font-black text-xl">中堅投稿者 B</span>
        </div>
        <div class="absolute top-[450px] left-[30px] w-[180px] py-4 glass border-slate-700 rounded-lg text-center">
            <span class="text-sky-400 text-sm font-bold block">NEWBIE</span>
            <span class="text-white font-black text-xl">新人動画 1</span>
        </div>
        <div class="absolute top-[450px] right-[30px] w-[180px] py-4 glass border-slate-700 rounded-lg text-center">
            <span class="text-sky-400 text-sm font-bold block">NEWBIE</span>
            <span class="text-white font-black text-xl">新人動画 2</span>
        </div>
        <div class="absolute bottom-[20px] left-[410px] w-[180px] py-4 glass border-slate-700 rounded-lg text-center">
            <span class="text-sky-400 text-sm font-bold block">NEWBIE</span>
            <span class="text-white font-black text-xl">新人動画 3</span>
        </div>

        <!-- キャプション -->
        <div class="absolute bottom-[-40px] w-full text-center">
            <p class="text-slate-400 text-2xl font-bold italic">
                「1本が短い」から、関連動画へ次々と視聴者が流れ込む
            </p>
        </div>
    </div>

</body>
</html>
"""

output_path = "results/visualization_radial_flow.html"
os.makedirs("results", exist_ok=True)
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"回遊性視覚化HTMLを作成しました: {output_path}")
