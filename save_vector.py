import os
from langchain_community.vectorstores.elasticsearch import ElasticsearchStore
from langchain.chains import RetrievalQA
from langchain.embeddings import HuggingFaceEmbeddings

embedding = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-large")
ELASTIC_PASSWORD = os.environ.get('ELASTIC_PASSWORD')

elastic_vector_search = ElasticsearchStore(
    es_url="http://localhost:9200",
    index_name="test_index",
    embedding=embedding,
    es_user="elastic",
    es_password=ELASTIC_PASSWORD
)


db = ElasticsearchStore.from_documents(
    docs,
    embedding=embedding,
    es_url="http://localhost:9200",
    index_name="test-basic",
)