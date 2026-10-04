import pickle
from datetime import datetime, timedelta, timezone
from pathlib import Path
from nicovideo_api_client.api.v2.snapshot_search_api_v2 import SnapshotSearchAPIV2
from nicovideo_api_client.constants import FieldType

# 取得件数の上限（十分大きな値を設定）
LIMIT = 10 * 1000 * 1000
# タイムアウト設定（全動画取得のため大幅に増量、または実質無制限に）
TIMEOUT = 3600 * 24

def main():
    print("category: all_2025")
    category = "all_2025"

    print("Fetching data for 2025 using modified library (auto-shifting range)...")

    # JST タイムゾーンの設定
    JST = timezone(timedelta(hours=9))

    # APIリクエストの構築
    # 修正版ライブラリが startTime を使って自動的に範囲をずらすため、
    # reverse=False (+startTime) でソートしておく必要があります。
    request = (
        SnapshotSearchAPIV2()
        .targets({FieldType.TITLE})
        .no_keyword()
        .field(
            {
                FieldType.CONTENT_ID,
                FieldType.TITLE,
                FieldType.USER_ID,
                FieldType.VIEW_COUNTER,
                FieldType.LENGTH_SECONDS,
                FieldType.START_TIME,
                FieldType.LIKE_COUNTER,
                FieldType.TAGS,
                FieldType.GENRE
            }
        )
        .sort(FieldType.START_TIME, reverse=False)
        .simple_filter()
        .filter(
            {
                FieldType.START_TIME: {
                    "gte": datetime(2025, 1, 1, 0, 0, 0, tzinfo=JST),
                    "lt": datetime(2026, 1, 1, 0, 0, 0, tzinfo=JST),
                }
            }
        )
        .limit(LIMIT)
        .user_agent("NicoApiClient", "3.0.1")
    )

    # APIの実行
    try:
        recv = request.request(timeout=TIMEOUT)
        data = recv.json()

        print(f"Total count reported by API: {data.get('meta', {}).get('totalCount')}")
        print(f"Total items actually fetched: {len(data.get('data', []))}")

        # 結果の保存
        Path("results").mkdir(exist_ok=True)
        output_path = f"results/{category}.pickle"
        with open(output_path, "wb") as f:
            pickle.dump(data, f)
        
        print(f"Results saved to {output_path}")

    except Exception as e:
        print(f"An error occurred during fetching: {e}")

if __name__ == "__main__":
    main()
