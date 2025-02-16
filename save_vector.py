import os
from datetime import datetime
from pathlib import Path
from tqdm import tqdm

from elasticsearch import Elasticsearch
from langchain_community.vectorstores import ElasticsearchStore
from langchain.chains import RetrievalQA
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter, Document

from pdfloader import pdf2txt_page_split


embedding = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-large")
ELASTIC_PASSWORD = os.environ.get('ELASTIC_PASSWORD')
FINGER_PRINT = "your_fingerprint"
CA_CERT = "/etc/elasticsearch/certs/http_ca.crt"

es = Elasticsearch(["https://localhost:9200"],
                   ca_certs=CA_CERT,
                   basic_auth=("elastic", ELASTIC_PASSWORD),
                   ssl_assert_fingerprint=FINGER_PRINT
                   )

"""
elastic_vector_search = ElasticsearchStore(
    index_name="test_index",
    es_connection=es,
    embedding=embedding
)
"""

def load_pdf(pdf_path: Path) -> list[Document]:
    documents = pdf2txt_page_split(pdf_path)  # ページごとのテキストをリストとして返す
    all_docs = []
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)

    for page, text in enumerate(documents):
        # テキストをDocumentオブジェクトに変換
        doc = Document(page_content=text, metadata={"page": page + 1, "title": pdf_path.stem})

        # Documentをチャンクに分割
        docs = text_splitter.split_documents([doc])

        for i, split_doc in enumerate(docs):
            # メタデータの追加
            split_doc.metadata["position"] = i
            split_doc.metadata["date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            split_doc.metadata["source_type"] = "pdf"
            all_docs.append(split_doc)

    return all_docs

        
def save_vector(docs):
    db = ElasticsearchStore.from_documents(
        docs,
        embedding=embedding,
        index_name="pmda",
        es_connection=es,
    )

def process_all_pdfs(directory_path):
    pdf_directory = Path(directory_path)
    pdf_files = list(pdf_directory.glob('*.pdf'))  # PDFファイルのリストを取得

    # tqdmでプログレスバーを初期化
    with tqdm(total=len(pdf_files), desc="Processing PDFs") as progress_bar:
        for pdf_file in pdf_files:
            print(f"Processing {pdf_file.name}...")
            docs = load_pdf(pdf_file)
            save_vector(docs)
            print(f"Completed processing {pdf_file.name}")

            progress_bar.update(1)  # プログレスバーを更新

if __name__ == '__main__':
    pdf_dir_list = ["/home/nagashimadaichi/pmda/pmda_all_pdf_20240109/PDF", 
                    "/home/nagashimadaichi/pmda/pmda_all_pdf_20240109-2/PDF",
                    "/home/nagashimadaichi/pmda/pmda_all_pdf_20240109-3/PDF",
                    "/home/nagashimadaichi/pmda/pmda_all_pdf_20240109-4/PDF"]
    
    for pdf_dir in pdf_dir_list:
        process_all_pdfs(pdf_dir)
        print("done")

