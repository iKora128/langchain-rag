from elasticsearch import Elasticsearch
import os

# Elasticsearch クライアントの設定
ELASTIC_PASSWORD = os.environ.get('ELASTIC_PASSWORD')
FINGER_PRINT = "your_fingerprint"
CA_CERT = "/etc/elasticsearch/certs/http_ca.crt"

es = Elasticsearch(["https://localhost:9200"],
                   ca_certs=CA_CERT,
                   basic_auth=("elastic", ELASTIC_PASSWORD),
                   ssl_assert_fingerprint=FINGER_PRINT
                   )

# インデックス名を指定
index_name = "medical_kuromoji"

# 既存のインデックスがあれば削除
if es.indices.exists(index=index_name):
    es.indices.delete(index=index_name)

# インデックスの設定とマッピング
index_settings = {
    "settings": {
        "analysis": {
            "analyzer": {
                "medical_ja": {
                    "tokenizer": "kuromoji_tokenizer",
                    "filter": [
                        "kuromoji_baseform",
                        "kuromoji_part_of_speech",
                        "ja_stop",
                        "kuromoji_stemmer",
                        "lowercase"
                    ]
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "title": {
                "type": "text",
                "analyzer": "medical_ja"
            },
            "content": {
                "type": "text",
                "analyzer": "medical_ja"
            }
        }
    }
}

# インデックス作成
es.indices.create(index=index_name, body=index_settings)

# サンプルドキュメントの登録
sample_docs = [
    {
        "title": "小児の解熱剤使用について",
        "content": "アセトアミノフェンは小児の発熱に対して一般的に使用される解熱鎮痛薬です。"
                  "通常、15mg/kgを目安に投与します。"
                  "ただし、重度の肝機能障害がある場合は禁忌となります。"
    },
    {
        "title": "インフルエンザの治療",
        "content": "インフルエンザに対しては、発症後48時間以内の抗ウイルス薬の投与が推奨されます。"
                  "解熱剤としてアセトアミノフェンを使用することがありますが、"
                  "サリチル酸系解熱鎮痛薬は、小児のインフルエンザではライ症候群の危険があるため使用を避けます。"
    }
]

# bulk insertのためのデータ準備
bulk_data = []
for doc in sample_docs:
    # インデックス操作のメタデータ
    bulk_data.append({
        "index": {
            "_index": index_name
        }
    })
    # ドキュメントデータ
    bulk_data.append(doc)

# bulk insertの実行
if bulk_data:
    es.bulk(operations=bulk_data)

# 検索クエリの実行例
search_queries = [
    "小児 解熱剤",
    "インフルエンザ 治療",
    "解熱剤 禁忌"
]

for query_text in search_queries:
    query = {
        "query": {
            "multi_match": {
                "query": query_text,
                "fields": ["title", "content"]
            }
        }
    }

    res = es.search(index=index_name, body=query)
    print(f"\n検索クエリ: {query_text}")
    for hit in res['hits']['hits']:
        print(f"スコア: {hit['_score']}")
        print(f"タイトル: {hit['_source']['title']}")
        print(f"内容: {hit['_source']['content'][:100]}...") 