# nico-analyzer (ニコニコ動画 年次統計ツール)

[スナップショット検索API v2](https://site.nicovideo.jp/search-api-docs/snapshot)を使用して、ニコニコ動画の特定カテゴリ（タグ・キーワード）の統計を取得し、可視化するスクリプト群です。

## 動作要件
- Python 3.11以上 (`tomllib` を使用するため)
- 日本語フォント環境 (`matplotlib-fontja` を使用)

## セットアップ
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 使い方

### 1. カテゴリの設定
`config.toml` を編集し、取得したいキーワードやグラフのタイトルを設定します。

### 2. データの取得
```powershell
python getter.py [category]
```
`results/[category].pickle` に検索結果が保存されます。

### 3. データの解析・可視化
```powershell
python analyzer.py [category]
```
`results/` ディレクトリに以下のファイルが生成されます：
- `*_annual-both.png`: 投稿数と累計再生数の推移
- `*_annual-newcommer.png`: 新規投稿者数の推移
- `*_annual-distribution.png`: 再生数の分布（バイオリン図）
- `*_continuation.png`: デビュー年別の投稿継続率
- `*_lifespan.png`: 投稿者の活動期間分布
- `*_most_popular.csv`: 各年の最多再生動画リスト

### 4. その他の機能
- **長期活動者の抽出**: 
  ```powershell
  python get_longest_active_users.py [category]
  ```
  現役で活動している期間が長いユーザーTop 50を表示します。
- **一括処理**: 
  `get_all.ps1`, `analyze_all.ps1` を実行することで、configに定義された複数のカテゴリをまとめて処理できます。

## ディレクトリ構成
- `results/`: 取得したデータおよび解析結果の保存先
- `config.toml`: カテゴリ定義（タイトル、検索キーワード、グラフ描画設定）