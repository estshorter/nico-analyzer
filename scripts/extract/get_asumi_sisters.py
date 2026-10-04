# /// script
# dependencies = [
#   "nicovideo-api-client",
# ]
# ///

from enum import Enum
from pathlib import Path
import pickle

from nicovideo_api_client.api.v2.snapshot_search_api_v2 import SnapshotSearchAPIV2
from nicovideo_api_client.constants import FieldType

LIMIT = 10 * 1000 * 1000
TIMEOUT = 800.0 * 2


class ExtendedFieldType(Enum):
    CONTENT_TYPE = "contentType"


def fetch_asumi_data(
    query: str = "彩澄 OR しゅおりり",
    output_path: str = "results/asumi_sisters.pickle"
):
    """
    ニコニコ動画スナップショット検索API v2から「彩澄 OR しゅおりり」を含むタグの動画全件を取得する。
    getter.pyの構造を踏襲しつつ、複合タグ（彩澄りりせ実況プレイ等）を漏れなく取得するため
    targetsにFieldType.TAGS（タグ部分一致）を指定する。
    """
    print(f"Fetching data for query: '{query}' (partial tag search)...")

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
                FieldType.LENGTH_SECONDS,
                FieldType.START_TIME,
                FieldType.LIKE_COUNTER,
                FieldType.TAGS,
                FieldType.GENRE,
                ExtendedFieldType.CONTENT_TYPE,
            }
        )
        .sort(FieldType.START_TIME, reverse=False)
        .no_filter()
        .limit(LIMIT)
        .user_agent("NicoApiClient", "3.0.1")
    )

    recv = request.request(timeout=TIMEOUT)
    res_json = recv.json()

    meta = res_json.get("meta", {})
    total_count = meta.get("totalCount", 0)
    data = res_json.get("data", [])
    print(f"Retrieved {len(data)} records (totalCount: {total_count}).")

    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "wb") as f:
        pickle.dump(res_json, f)

    print(f"Saved snapshot response to {out_file.resolve()}")
    return res_json


if __name__ == "__main__":
    fetch_asumi_data()
