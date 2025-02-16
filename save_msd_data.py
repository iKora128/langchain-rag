from pathlib import Path
import json

from langchain_community.vectorstores import ElasticsearchStore
from langchain.chains import RetrievalQA
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter, Document


from save_vector import save_vector


def set_metadata(json_path="/home/nagashimadaichi/develop/assets/msd.json"):
    with open(json_path, "r", encoding="utf-8") as f:
        articles = json.load(f)

    all_docs = []
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)

    for article in articles:
        # JSONデータの各記事をDocumentオブジェクトに変換

        # 各articleの型を確認
        if not isinstance(article, dict):
            print(f"article: {article}")
            print(f"Expected a dict, but got: {type(article)}")
            continue

        doc = Document(page_content=article["text"], metadata={
            "date": article["date"],
            "link": article["link"],
            "topic": article["topic"],
            "category": article["category"],
            "title": article["title"],
            "source_type": "web_article"
        })

        # Documentをチャンクに分割
        docs = text_splitter.split_documents([doc])

        for i, split_doc in enumerate(docs):
            # メタデータに位置情報を追加
            split_doc.metadata["position"] = i
            all_docs.append(split_doc)

    return all_docs

if __name__ == '__main__':
    docs = set_metadata()
    save_vector(docs)
