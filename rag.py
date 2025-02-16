import os
from elasticsearch import Elasticsearch

from langchain_community.vectorstores.elasticsearch import ElasticsearchStore
from langchain.chains import RetrievalQA
from langchain_community.embeddings import HuggingFaceEmbeddings

embedding = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-large")
ELASTIC_PASSWORD = os.environ.get('ELASTIC_PASSWORD')
FINGER_PRINT = "your_fingerprint"
CA_CERT = "/etc/elasticsearch/certs/http_ca.crt"

es = Elasticsearch(["https://localhost:9200"],
                   ca_certs=CA_CERT,
                   basic_auth=("elastic", ELASTIC_PASSWORD),
                   ssl_assert_fingerprint=FINGER_PRINT
                   )

elastic_vector_search = ElasticsearchStore(
    es_url="http://localhost:9200",
    index_name="pmda",
    embedding=embedding,
    es_connection=es
)

query = "小児の発熱に対しての解熱剤とその禁忌について教えてください"
results = elastic_vector_search.similarity_search(query)
print(results)

