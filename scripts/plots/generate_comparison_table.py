
import os

html_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', 'Noto Sans JP', sans-serif; }
        .glass { background: rgba(10, 15, 30, 0.9); backdrop-filter: blur(16px); }
        .neon-red { text-shadow: 0 0 15px rgba(255, 79, 129, 0.6); }
        .neon-blue { text-shadow: 0 0 15px rgba(79, 172, 254, 0.6); }
    </style>
</head>
<body class="bg-slate-950 p-12 flex items-center justify-center min-h-screen">
    <div class="glass border border-slate-700 shadow-2xl overflow-hidden">
        <table class="text-left border-collapse">
            <thead>
                <tr class="bg-slate-900 border-b-2 border-slate-700">
                    <th class="px-12 py-12 text-white text-4xl font-black tracking-widest uppercase border-r border-slate-700">項目</th>
                    <th class="px-20 py-12 text-rose-400 text-5xl font-black tracking-widest text-center border-r border-slate-700">ボイロキッチン</th>
                    <th class="px-20 py-12 text-sky-400 text-5xl font-black tracking-widest text-center">ボイロ車載</th>
                </tr>
            </thead>
            <tbody class="divide-y divide-slate-800">
                <tr>
                    <td class="px-12 py-12 font-bold text-slate-300 text-4xl border-r border-slate-800">定期投稿</td>
                    <td class="px-20 py-12 text-center border-r border-slate-800">
                        <div class="text-rose-500 font-black text-7xl neon-red">易 (日常)</div>
                    </td>
                    <td class="px-20 py-12 text-center">
                        <div class="text-sky-500 font-bold text-6xl neon-blue">難 (遠征)</div>
                    </td>
                </tr>
                <tr>
                    <td class="px-12 py-12 font-bold text-slate-300 text-4xl border-r border-slate-800">回転率</td>
                    <td class="px-20 py-12 text-center border-r border-slate-800">
                        <div class="text-rose-500 font-black text-7xl neon-red">高 (4分)</div>
                    </td>
                    <td class="px-20 py-12 text-center">
                        <div class="text-sky-500 font-bold text-6xl neon-blue">低 (8分〜)</div>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</body>
</html>
"""

output_path = "results/table_strategy_comparison.html"
os.makedirs("results", exist_ok=True)
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"比較表HTMLを更新しました: {output_path}")
