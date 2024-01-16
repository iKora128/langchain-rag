from langchain_community.vectorstores.elasticsearch import ElasticsearchStore
from langchain.chains import RetrievalQA
from langchain.embeddings import HuggingFaceEmbeddings

embedding = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-large")

elastic_vector_search = ElasticsearchStore(
    es_url="http://localhost:9200",
    index_name="test_index",
    embedding=embedding
)

