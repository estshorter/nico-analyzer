import pandas as pd
from pathlib import Path

OUT_DIR = Path("results/simple_onboard")

def make_table(csv_path, top_n=10):
    if not Path(csv_path).exists():
        return "*データなし*"
    df = pd.read_csv(csv_path)
    lines = []
    lines.append("| 順位 | ユーザー名 | 車載ブランク | ボイロ活動ブランク | 前回車載投稿日 | 投稿祭動画タイトル |")
    lines.append("| :---: | :--- | :---: | :---: | :---: | :--- |")
    
    for idx, r in df.head(top_n).iterrows():
        rank = idx + 1
        name = r['user_name']
        
        days_ob = r['days_gap_ob'] if 'days_gap_ob' in r and not pd.isna(r['days_gap_ob']) else r['days_gap']
        days_st = r['days_gap_st'] if 'days_gap_st' in r and not pd.isna(r['days_gap_st']) else days_ob
        
        def fmt_gap(days):
            years_approx = round(days / 365.25, 1)
            months_approx = round(days / 30.44, 1)
            if days >= 365:
                return f"**{days:,.1f}日 (約{years_approx}年)**"
            elif days >= 30:
                return f"**{days:,.1f}日 (約{months_approx}ヶ月)**"
            else:
                return f"**{days:,.1f}日**"
                
        gap_ob_str = fmt_gap(days_ob)
        gap_st_str = fmt_gap(days_st)
            
        last_date = str(r['last_ob_time']).split(' ')[0]
        title = r['so_title']
        
        lines.append(f"| **{rank}** | **{name}** | {gap_ob_str} | {gap_st_str} | {last_date} | {title} |")
        
    return "\n".join(lines)

def make_tanabata_table(csv_path):
    if not Path(csv_path).exists():
        return "*データなし*"
    df = pd.read_csv(csv_path)
    lines = []
    lines.append("| 順位 | ユーザー名 | 参加回数 | 参加年 | 代表・最新投稿動画タイトル |")
    lines.append("| :---: | :--- | :---: | :---: | :--- |")
    for idx, r in df.iterrows():
        rank = idx + 1
        name = r['user_name']
        cnt = f"**{r['simple_onboard_count']}回**"
        years = str(r['participated_years'])
        title = r['latest_video_title']
        lines.append(f"| **{rank}** | **{name}** | {cnt} | {years} | {title} |")
    return "\n".join(lines)

def update_reports():
    t_2023_ret = make_table(OUT_DIR / "top50_longest_gap_2023.csv")
    t_2024_ret = make_table(OUT_DIR / "top50_longest_gap_2024.csv")
    t_2025_ret = make_table(OUT_DIR / "top50_longest_gap_2025.csv")
    t_2026_ret = make_table(OUT_DIR / "top50_longest_gap_2026.csv")
    
    t_2023_reg = make_table(OUT_DIR / "top50_gap_regular_2023.csv")
    t_2024_reg = make_table(OUT_DIR / "top50_gap_regular_2024.csv")
    t_2025_reg = make_table(OUT_DIR / "top50_gap_regular_2025.csv")
    t_2026_reg = make_table(OUT_DIR / "top50_gap_regular_2026.csv")
    
    t_tanabata_st = make_tanabata_table(OUT_DIR / "tanabata_creators_voiceroid.csv")
    t_tanabata_ob = make_tanabata_table(OUT_DIR / "tanabata_creators_onboard.csv")
    
    df_sum = pd.read_csv(OUT_DIR / "summary_metrics.csv")
    
    def get_val(row_idx, col_name):
        return df_sum[col_name].iloc[row_idx]

    report_content = f"""# シンプル車載動画投稿祭 データ分析レポート (2023〜2026)

`D:\\動画投稿\\台本まとめ\\12_シンプル車載.md` に基づき、ニコニコ動画における「シンプル車載動画投稿祭」（2023年〜2026年）の全投稿データおよび参加クリエイターの動向を詳細に集計・分析しました。

> **2024年の開催期間について**: 2024年6月〜8月のニコニコ動画サービス停止（サイバー攻撃の影響）に伴い、第2回（2024年）は当初予定（7/2〜7/16）から **2024年8月19日〜9月2日** に延期して開催されました。

---

## 1. 投稿祭の基本情報と目的

### 投稿祭のコンセプト
- **初心者**: 投稿しやすく
- **失踪者**: 復帰しやすく
- **常連者**: 少し変化球で
- **視聴者**: 視聴しやすく

### 集計対象期間
- **2023年（第1回）**: 2023/07/04 0:00 〜 2023/07/18 0:00
- **2024年（第2回・延期開催）**: 2024/08/19 0:00 〜 2024/09/02 0:00 *(※ニコニコ復旧後)*
- **2025年（第3回）**: 2025/07/08 0:00 〜 2025/07/22 0:00
- **2026年（第4回）**: 2026/07/07 0:00 〜 2026/07/21 0:00

---

## 2. 年次サマリー＆クリエイター構成

### クリエイター構成比（割合）
![クリエイター構成比グラフ](creator_composition_stacked.png)

### クリエイター属性推移（絶対値：人数）
#### 【車載視点】
![クリエイター人数推移折れ線グラフ（車載視点）](creator_composition_absolute_onboard.png)

#### 【ボイロ活動視点】
![クリエイター人数推移折れ線グラフ（ボイロ活動視点）](creator_composition_absolute_voiceroid.png)

### 集計結果一覧

| 項目 | 2023年 (第1回) | 2024年 (第2回) | 2025年 (第3回) | 2026年 (第4回) |
| :--- | :---: | :---: | :---: | :---: |
| **開催期間内の動画数** | **{get_val(0, 'period_videos')}本** | **{get_val(1, 'period_videos')}本** | **{get_val(2, 'period_videos')}本** | **{get_val(3, 'period_videos')}本** |
| **参加クリエイター数** | **{get_val(0, 'period_creators')}人** | **{get_val(1, 'period_creators')}人** | **{get_val(2, 'period_creators')}人** | **{get_val(3, 'period_creators')}人** |
| **年間タグ登録総動画数** | {get_val(0, 'calendar_videos')}本 | {get_val(1, 'calendar_videos')}本 | {get_val(2, 'calendar_videos')}本 | {get_val(3, 'calendar_videos')}本 |
| **①-A 初投稿者数** *(車載初投稿)* | **{get_val(0, 'first_time_count')}人 ({get_val(0, 'first_time_pct')}%)** | **{get_val(1, 'first_time_count')}人 ({get_val(1, 'first_time_pct')}%)** | **{get_val(2, 'first_time_count')}人 ({get_val(2, 'first_time_pct')}%)** | **{get_val(3, 'first_time_count')}人 ({get_val(3, 'first_time_pct')}%)** |
| **①-B 初投稿者数** *(ボイロ活動初投稿)* | **{get_val(0, 'first_time_st_count')}人 ({get_val(0, 'first_time_st_pct')}%)** | **{get_val(1, 'first_time_st_count')}人 ({get_val(1, 'first_time_st_pct')}%)** | **{get_val(2, 'first_time_st_count')}人 ({get_val(2, 'first_time_st_pct')}%)** | **{get_val(3, 'first_time_st_count')}人 ({get_val(3, 'first_time_st_pct')}%)** |
| **②-A 復帰者数** *(車載復帰: >1年ブランク)* | **{get_val(0, 'returning_count')}人 ({get_val(0, 'returning_pct')}%)** | **{get_val(1, 'returning_count')}人 ({get_val(1, 'returning_pct')}%)** | **{get_val(2, 'returning_count')}人 ({get_val(2, 'returning_pct')}%)** | **{get_val(3, 'returning_count')}人 ({get_val(3, 'returning_pct')}%)** |
| **②-B 復帰者数** *(ボイロ活動復帰: >1年ブランク)* | **{get_val(0, 'returning_st_count')}人 ({get_val(0, 'returning_st_pct')}%)** | **{get_val(1, 'returning_st_count')}人 ({get_val(1, 'returning_st_pct')}%)** | **{get_val(2, 'returning_st_count')}人 ({get_val(2, 'returning_st_pct')}%)** | **{get_val(3, 'returning_st_count')}人 ({get_val(3, 'returning_st_pct')}%)** |
| **③-A 常連・継続投稿者数** *(車載視点)* | {get_val(0, 'regular_count')}人 ({get_val(0, 'regular_pct')}%) | {get_val(1, 'regular_count')}人 ({get_val(1, 'regular_pct')}%) | {get_val(2, 'regular_count')}人 ({get_val(2, 'regular_pct')}%) | {get_val(3, 'regular_count')}人 ({get_val(3, 'regular_pct')}%) |
| **③-B 常連・継続投稿者数** *(ボイロ活動視点)* | {get_val(0, 'regular_st_count')}人 ({get_val(0, 'regular_st_pct')}%) | {get_val(1, 'regular_st_count')}人 ({get_val(1, 'regular_st_pct')}%) | {get_val(2, 'regular_st_count')}人 ({get_val(2, 'regular_st_pct')}%) | {get_val(3, 'regular_st_count')}人 ({get_val(3, 'regular_st_pct')}%) |
| **④ 前年参加者の翌年失踪率 (車載無投稿)** | — | **{get_val(1, 'disappeared_ob_pct')}% ({get_val(1, 'disappeared_ob_count')}/{get_val(1, 'prev_year_creators')}人)** | **{get_val(2, 'disappeared_ob_pct')}% ({get_val(2, 'disappeared_ob_count')}/{get_val(2, 'prev_year_creators')}人)** | **{get_val(3, 'disappeared_ob_pct')}% ({get_val(3, 'disappeared_ob_count')}/{get_val(3, 'prev_year_creators')}人)** |
| **⑤ 前年参加者の翌年失踪率 (ボイロ活動無投稿)** | — | **{get_val(1, 'disappeared_st_pct')}% ({get_val(1, 'disappeared_st_count')}/{get_val(1, 'prev_year_creators')}人)** | **{get_val(2, 'disappeared_st_pct')}% ({get_val(2, 'disappeared_st_count')}/{get_val(2, 'prev_year_creators')}人)** | **{get_val(3, 'disappeared_st_pct')}% ({get_val(3, 'disappeared_st_count')}/{get_val(3, 'prev_year_creators')}人)** |

> **分析ポイント**:
> 1. **安定したコミュニティ規模**: 毎年265名〜313名のクリエイター（動画数267〜313本）が参加し、非常に安定した文化として定着しています。
> 2. **初心者の継続的な流入**: 毎年20〜50名（8〜16%）のボイロ車載初投稿者が参加し、車載カテゴリの新たな登竜門として機能しています。
> 3. **失踪予防効果**: 翌年の車載失踪率は10〜15%程度と非常に低く、約85%以上の投稿者が翌年も投稿を継続しています。

---

## 3. 日別投稿数の推移 (1日目〜15日目)

![日別投稿数推移グラフ](daily_post_counts_trend.png)

各年の開催初日から最終日（15日目）までの日別投稿数推移です。初日と最終日に投稿が集中するダブルピーク型の構造が見られます。

---

## 4. ブランク期間（経過日数）の分布と見せ方

### パターンA：4段サブプロット（年別比較に最適・推奨）
![4段サブプロット対数ヒストグラム](days_gap_histogram_log_subplots.png)

### パターンB：全期間合算単一グラフ（全体傾向の提示に最適・推奨）
![全期間合算対数ヒストグラム](days_gap_histogram_log_combined.png)

---

## 5. ブランク期間ランキング (復帰者版 ＆ 常連・継続投稿者版)

> **ブランク期間の2軸定義**:
> - **車載ブランク**: 前回の車載動画投稿からの経過日数（車載動画制作への復帰・投稿間隔）
> - **ボイロ活動ブランク**: 前回のソフトウェアトーク動画投稿からの経過日数（他ジャンル含むボイロ動画制作活動全体への復帰・投稿間隔）
> 
> ※「車載ブランクが長くてボイロ活動ブランクが短期間」の場合、普段はゲーム実況や旅行動画などを投稿している現役クリエイターが久しぶりに車載動画へ帰ってきた「車載ジャンル回帰組」であることを意味します。

### 【A】復帰者版 TOP 10 (>1年ブランクかつ前年不参加)

#### 2023年（復帰者）
{t_2023_ret}

#### 2024年（復帰者）
{t_2024_ret}

#### 2025年（復帰者）
{t_2025_ret}

#### 2026年（復帰者）
{t_2026_ret}

---

### 【B】常連・継続投稿者版 TOP 10 (ブランクが長い順)

#### 2023年（常連・継続投稿者）
{t_2023_reg}

#### 2024年（常連・継続投稿者）
{t_2024_reg}

#### 2025年（常連・継続投稿者）
{t_2025_reg}

#### 2026年（常連・継続投稿者）
{t_2026_reg}

---

## 6. データから読み解く考察・深掘り分析

### 考察1: 「シンプル」というレギュレーションが壊した編集の壁
ボイロ車載動画は本来「動画撮影・GPSログ・立ち絵アニメーション・店舗解説」など編集コストが非常に高いジャンルです。編集の簡略化を推奨する本企画が、「車載動画を作ってみたいが編集が大変そう」と躊躇していた他ジャンル投稿者（ゲーム実況やキッチン動画手など）の参入ハードルを劇的に引き下げたと考察できます。

### 考察2: 数年越しの「伝説の復帰劇」を生み出す復活装置
毎年10〜16名の長期休止クリエイターが復帰しています。「短くてシンプルで良い」という手軽さが、一度途切れた投稿者の車載動画復帰のきっかけとして完璧に機能しています。

### 考察3: 2024年「ニコニコ停止障害」を跳ね返した熱量
2024年6〜8月のサイバー攻撃障害に伴い第2回は8月19日〜9月2日に延期されましたが、サービス再開直後にもかかわらず初日だけで66本が集中し、年間通算346本を記録しました。

### 考察4: 投稿行動の心理「ダブルピーク構造」
15日間の日別投稿数は毎年「初日」と「最終盤（14〜15日目）」に集中するダブルピーク型を示します。「シンプルだからこそ、締め切り数日前に思い立って作っても最終日に間に合う」という投稿祭ならではの特性が現れています。

### 考察5: 驚異的な低失踪率（定着率約85〜90%）
参加者の翌年車載失踪率は10%〜15%程度です。参加者の約85〜90%が投稿を継続しており、ニコニコの車載カテゴリ全体を活性化・持続させるエコシステムとして大成功を収めています。

### 考察6: 投稿祭限定で現れる「純度100%の七夕投稿者」の存在
複数回（2回以上）シンプル車載動画投稿祭に参加しているリピーター300名のうち、**過去の全期間を通じて「シンプル車載動画投稿祭」以外の動画（他車載動画や他ジャンルボイロ動画）を1本も投稿していない「純度100%の七夕投稿者」が11名（ボイロ活動視点 / 車載視点では14名）存在**します。
代表例として、4年間（2023〜2026年）連続で参加している「セリス」様など、平時は動画を投稿せず「年に1回のシンプル車載動画投稿祭の時だけ動画を作って帰ってくる」という特有の活動スタイルを持つクリエイター層を繋ぎ止める重要なイベントとして機能していることが数値でも実証されています。

#### 【純度100%の七夕投稿者一覧 (ボイロ活動視点：他動画0本)】
{t_tanabata_st}

---

## 7. 動画台本の構成ストーリー案（動画制作向け）

1. **導入（オープニング）**: シンプル車載動画投稿祭のコンセプトと目的の振り返り
2. **章1（規模と勢い）**: 2024年ニコニコ停止障害を跳ね返した熱量 ＆ 日別ダブルピーク現象
3. **章2（初投稿者の壁破壊）**: 毎年誕生する車載初投稿者！他ジャンル投稿者を惹きつけた理由
4. **章3（感動の復帰劇＆七夕投稿者）**: 数年ぶりの復活！？＆投稿祭限定で現れる「純度100%七夕投稿者」
5. **章4（カテゴリへの功績）**: 失踪率わずか10%台！シンプル車載がもたらした車載動画界への影響
6. **結び（エンディング）**: まとめと今後の期待

---

## 8. 失踪率（継続性）の分析

![失踪率グラフ](disappearance_rates.png)

各年の投稿祭に参加したクリエイターのうち、その後一度も動画を投稿していない人の人数および割合です。

---

## 9. 保存ファイル・再利用可能なスクリプト一覧

- **集計用スクリプト**: [analyze_simple_onboard.py](file:///C:/Users/estshorter/src/nico-analyzer/analyze_simple_onboard.py)
- **七夕投稿者抽出スクリプト**: [analyze_tanabata_creators.py](file:///C:/Users/estshorter/src/nico-analyzer/analyze_tanabata_creators.py)
- **グラフ描画スクリプト**: [plot_simple_onboard.py](file:///C:/Users/estshorter/src/nico-analyzer/plot_simple_onboard.py)
- **同期用スクリプト**: [generate_markdown_tables.py](file:///C:/Users/estshorter/src/nico-analyzer/generate_markdown_tables.py)
- **生成データ (CSV)**:
  - [summary_metrics.csv](file:///C:/Users/estshorter/src/nico-analyzer/results/simple_onboard/summary_metrics.csv) (年次サマリーデータ)
  - [all_user_gaps.csv](file:///C:/Users/estshorter/src/nico-analyzer/results/simple_onboard/all_user_gaps.csv) (全参加者の経過日数データ)
  - [tanabata_creators_voiceroid.csv](file:///C:/Users/estshorter/src/nico-analyzer/results/simple_onboard/tanabata_creators_voiceroid.csv) (純度100%七夕投稿者リスト)
  - [top50_longest_gap_2023.csv](file:///C:/Users/estshorter/src/nico-analyzer/results/simple_onboard/top50_longest_gap_2023.csv) ~ [2026.csv](file:///C:/Users/estshorter/src/nico-analyzer/results/simple_onboard/top50_longest_gap_2026.csv) (復帰者>1年TOP50)
  - [top50_gap_regular_2023.csv](file:///C:/Users/estshorter/src/nico-analyzer/results/simple_onboard/top50_gap_regular_2023.csv) ~ [2026.csv](file:///C:/Users/estshorter/src/nico-analyzer/results/simple_onboard/top50_gap_regular_2026.csv) (常連・継続投稿者TOP50)
"""
    
    with open(OUT_DIR / "simple_onboard_analysis_report.md", "w", encoding="utf-8") as f:
        f.write(report_content)
        
    brain_path = Path("C:/Users/estshorter/.gemini/antigravity-cli/brain/432c4cb9-5c81-4f11-b346-aedc27fe1631/simple_onboard_analysis.md")
    with open(brain_path, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print("Report files regenerated including 2026 data.")

if __name__ == '__main__':
    update_reports()
