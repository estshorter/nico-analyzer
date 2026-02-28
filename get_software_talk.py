# /// script
# dependencies = [
#   "nicovideo-api-client",
# ]
# ///

import pickle
from pathlib import Path
from nicovideo_api_client.api.v2.snapshot_search_api_v2 import SnapshotSearchAPIV2
from nicovideo_api_client.constants import FieldType

# 取得件数の上限
LIMIT = 10 * 1000 * 1000
# タイムアウト設定
TIMEOUT = 800 * 16

def main():
    # 抽出対象のキーワード
    keywords = [
        "ソフトウェアトーク",
        "VOICEPEAK",
        "VOICEROID",
        "A.I.VOICE",
        "CeVIO",
        "VOICEVOX",
        "ガイノイドTalk",
        "CoeFont",
        "COEIROINK"
    ]
    
    # ORで結合してクエリを作成
    query = " OR ".join(keywords)
    category = "software_talk"

    print(f"Searching for: {query}")

    # APIリクエストの構築
    # .targets({FieldType.TAGS}) を使用することでタグの部分一致検索を行う
    request = (
        SnapshotSearchAPIV2()
        .targets({FieldType.TAGS})
        .single_query(query)
        .field(
            {
                FieldType.CONTENT_ID,
                FieldType.TITLE,
                FieldType.USER_ID,
                FieldType.VIEW_COUNTER,
                FieldType.START_TIME,
                FieldType.TAGS
            }
        )
        .sort(FieldType.START_TIME, reverse=True)
        .no_filter()
        .limit(LIMIT)
        .user_agent("NicoApiClient", "3.0.1")
    )

    # APIの実行
    recv = request.request(timeout=TIMEOUT)
    data = recv.json()

    print(f"Total count available: {data.get('meta', {}).get('totalCount')}")

    # 結果の保存
    Path("results").mkdir(exist_ok=True)
    output_path = f"results/{category}.pickle"
    with open(output_path, "wb") as f:
        pickle.dump(data, f)
    
    print(f"Results saved to {output_path}")
    print(f"Total items fetched: {len(recv.json().get('data', []))}")

if __name__ == "__main__":
    main()
