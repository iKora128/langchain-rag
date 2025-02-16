import os
from elasticsearch import Elasticsearch

ELASTIC_PASSWORD = os.environ.get('ELASTIC_PASSWORD')
FINGER_PRINT = "your_fingerprint"

# Elasticsearchサーバーのホストとポートを指定してクライアントを作成
es = Elasticsearch(["https://localhost:9200"],
                   basic_auth=("elastic", ELASTIC_PASSWORD),
                   ssl_assert_fingerprint=FINGER_PRINT,)

# インデックスの一覧を取得
indices = es.indices.get_alias(index="*")

query = {
    "query": """
FROM test_index
| LIMIT 10
"""
}

# 検索クエリの実行
response = es.search(index="test_index", body=query)

# 検索結果の表示
for doc in response['hits']['hits']:
    print(doc['_source'])

