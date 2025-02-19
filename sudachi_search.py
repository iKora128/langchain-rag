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
index_name = "medical_sudachi"

# 既存のインデックスがあれば削除
if es.indices.exists(index=index_name):
    es.indices.delete(index=index_name)

# インデックスの設定とマッピング
index_settings = {
    "settings": {
        "analysis": {
            "analyzer": {
                "medical_ja": {
                    "tokenizer": "sudachi_tokenizer",
                    "mode": "C",  # A（短い）、B（中間）、C（長い）の分割モード
                    "filter": [
                        "sudachi_part_of_speech",
                        "sudachi_normalizedform",
                        "sudachi_ja_stop",
                        "sudachi_baseform"
                    ],
                    "settings": {
                        "mode": "search",  # search または normal
                        "split_mode": "C",  # デフォルトの分割モード
                        "dictionary_type": "full"  # system または full
                    }
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
        "title": "抗生物質の適正使用",
        "content": "抗生物質の不適切な使用は、薬剤耐性（AMR）を引き起こす可能性があります。"
                  "特に広域スペクトラム抗生物質の使用は慎重に判断する必要があります。"
                  "起因菌が同定された場合は、狭域スペクトラムの抗生物質に変更することを検討します。"
    },
    {
        "title": "高血圧治療のガイドライン",
        "content": "高血圧の第一選択薬として、カルシウム拮抗薬、ARB、ACE阻害薬、利尿薬が推奨されます。"
                  "生活習慣の改善（減塩、運動、禁煙など）も重要な治療の一環です。"
                  "収縮期血圧140mmHg以上、拡張期血圧90mmHg以上を高血圧と定義します。"
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
    "抗生物質 耐性",
    "高血圧 治療",
    "生活習慣 改善"
]

for query_text in search_queries:
    query = {
        "query": {
            "multi_match": {
                "query": query_text,
                "fields": ["title", "content"],
                "type": "most_fields"
            }
        }
    }

    res = es.search(index=index_name, body=query)
    print(f"\n検索クエリ: {query_text}")
    for hit in res['hits']['hits']:
        print(f"スコア: {hit['_score']}")
        print(f"タイトル: {hit['_source']['title']}")
        print(f"内容: {hit['_source']['content'][:100]}...") 