import pickle
import sys
import tomllib
from pathlib import Path

from nicovideo_api_client.api.v2.snapshot_search_api_v2 import SnapshotSearchAPIV2
from nicovideo_api_client.constants import FieldType

LIMIT = 10 * 1000 * 1000


def main(category, query):
    # URL生成
    request = (
        SnapshotSearchAPIV2()
        .tags_exact()
        .single_query(query)
        .field(
            {
                FieldType.CONTENT_ID,
                FieldType.TITLE,
                FieldType.USER_ID,
                FieldType.VIEW_COUNTER,
                FieldType.MYLIST_COUNTER,
                FieldType.LIKE_COUNTER,
                FieldType.LENGTH_SECONDS,
                FieldType.START_TIME,
                FieldType.COMMENT_COUNTER,
            }
        )
        .sort(FieldType.START_TIME, reverse=True)
        .no_filter()
        .limit(LIMIT)
        .user_agent("NicoApiClient", "2.0.6")
    )

    # https://api.search.nicovideo.jp/api/v2/snapshot/video/contents/search?targets=tagsExact&q=VOCALOID&fields=contentId%2Ctitle&_sort=-viewCounter
    # print(request.build_url())

    # 実行
    # API のレスポンスが表示される
    recv = request.request()

    Path("results").mkdir(exist_ok=True)
    with open(f"results/{category}.pickle", "wb") as f:
        pickle.dump(recv.json(), f)


if __name__ == "__main__":
    args = sys.argv
    if len(args) == 2:
        with open("config.toml", "rb") as f:
            cfg = tomllib.load(f)
        main(args[1], cfg[args[1]]["keywords"])
    else:
        print("コマンドライン引数が少なすぎます")
