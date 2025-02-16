# RAG LangChain & Elasticsearch プロジェクト

このリポジトリは、[LangChain](https://github.com/hwchase17/langchain) と [Elasticsearch](https://www.elastic.co/elasticsearch/) を組み合わせた Retrieval-Augmented Generation (RAG) システムの実装例です。  
文書の埋め込み生成、PDFやWebからのデータ抽出、ベクトルインデックスへの格納、そしてセマンティック検索を行う仕組みを提供します。

## 概要

- **文書埋め込み**  
  HuggingFace の多言語モデル (`intfloat/multilingual-e5-large`) を利用して、文書の埋め込みを生成します。

- **PDF からのテキスト抽出**  
  [pdfminer](https://github.com/pdfminer/pdfminer.six) を用いて、PDFファイルからページごとにテキストを抽出・クリーンアップします。

- **Webスクレイピング (MSDデータ)**  
  [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) を用い、MSD（医療系）の記事データをスクレイピングしてJSONに変換します。

- **ベクトルインデックスと検索**  
  Elasticsearch に埋め込み済み文書を格納し、LangChain のラッパーを用いてセマンティック検索（類似度検索）を実現します。

- **サンプルスクリプトとユーティリティ**  
  Elasticsearch の接続確認や、PDF/MSDデータの処理、埋め込み生成、検索クエリの実行などを行うスクリプト群を含みます。

## ディレクトリ構成

```
ikora128-langchain-rag/
├── README.md                  
├── elasticsearch.txt  # Elasticsearch の起動、インストールのメモ
├── embed.py           # サンプルテキストの埋め込み生成スクリプト
├── pdfloader.py       # PDFからテキストを抽出（ページ単位での抽出など）
├── pyproject.toml             
├── rag.py         　   # RetrievalQAの例。Elasticsearch から類似文書検索を実施するスクリプト
├── requirements.txt   
├── save_msd_data.py
├── save_vector.py     # PDFのテキスト抽出、チャンク分割、Elasticsearch へのベクトル保存処理を行うスクリプト
├── uv.lock           
├── .python-version
├── assets/                 
└── scripts/            
    ├── es_test.py
    └── msd.py
```

## 各ファイルの役割

- **elasticsearch.txt**  
  Elasticsearch を起動するためのコマンドや、インスタンスの確認方法、インストールディレクトリに関する情報を記載しています。

- **embed.py**  
  HuggingFace の埋め込みモデルを用いて、サンプルテキストの埋め込みを生成する例です。LangChain のコミュニティ埋め込みモジュールの使い方を学ぶのに適しています。

- **pdfloader.py**  
  PDFファイルからテキストを抽出する関数群を提供します。  
  - `pdf2txt_page_split`: PDFをページごとに読み込み、テキストを抽出・クリーンアップしてリストで返す関数。  
  - `pdf2txt_all`: pdfminer の高レベルAPIを用いてPDF全体のテキストを抽出（標準出力に表示）。
  
- **rag.py**  
  Elasticsearch に接続し、LangChain の `ElasticsearchStore` を利用して、質問に対する類似文書検索（セマンティック検索）を実行するサンプルです。  
  環境変数や証明書、フィンガープリントなど、セキュリティ設定が必要な点に注意してください。

- **save_vector.py**  
  PDFファイルのテキストを抽出し、テキストをチャンクに分割、さらに各チャンクにメタデータ（ページ番号、処理日時、ソース種別など）を付加してElasticsearchにインデックスします。  
  複数のPDFディレクトリを処理するための `process_all_pdfs` 関数も提供しています。

- **save_msd_data.py**  
  MSDのJSON形式データを読み込み、各記事をLangChainの `Document` オブジェクトに変換、さらにチャンク分割を行い、ベクトル化してElasticsearchに保存します。

- **scripts/es_test.py**  
  Elasticsearch の接続状況と簡単な検索クエリの実行テストを行うスクリプトです。  
  インデックス一覧の取得や、指定したインデックス（例：`test_index`）からの検索結果を表示します。

- **scripts/msd.py**  
  MSD記事をスクレイピングするスクリプトです。  
  - 指定したURLからパンくずリスト（breadcrumb）を抽出し、記事のメタ情報（日付、リンク、トピック、カテゴリ、タイトル）を取得  
  - 記事本文を取得し、JSON形式にまとめて保存します。  
  また、カテゴリページやトピックページからリンクを抽出する関数も含まれています。

## 使い方

### 事前準備

1. **Python バージョン**  
   `.python-version` に記載されている通り、Python 3.12 以上を使用してください。

2. **依存パッケージのインストール**  
   以下のコマンドで必要なパッケージをインストールします。
   ```bash
   pip install -r requirements.txt
   ```
   または、Poetry や Pipenv などのツールを利用する場合は `pyproject.toml` を参照してください。

3. **Elasticsearch の設定**  
   - Elasticsearch（バージョン 8.11.0 以上）がインストールされ、`elasticsearch.txt` の指示に従いサービスを起動してください。
   - 各スクリプト内の `FINGER_PRINT` や `CA_CERT` の値は、ご利用の環境に合わせて適切に設定してください。
   - 環境変数 `ELASTIC_PASSWORD` を設定します。  
     例:
     ```bash
     export ELASTIC_PASSWORD=your_actual_elastic_password
     ```

### 各スクリプトの実行

1. **埋め込みのサンプル実行**  
   HuggingFace の埋め込みモデルを使ったサンプルとして、以下を実行します。
   ```bash
   python embed.py
   ```

2. **PDF の処理とベクトルインデックスの作成**  
   PDFファイルからテキストを抽出し、チャンク分割してElasticsearchに保存する場合は、以下を実行します。
   ```bash
   python save_vector.py
   ```
   ※ スクリプト内に指定されているPDFディレクトリを必要に応じて変更してください。

3. **MSDデータのインデックス化**  
   MSDのJSONファイル（フォーマットに沿ったデータ）をElasticsearchにインデックスする場合は、以下を実行します。
   ```bash
   python save_msd_data.py
   ```

4. **Retrieval QA の実行**  
   Elasticsearch にインデックスされた文書に対して質問を投げ、関連する文書を検索するには、以下を実行します。
   ```bash
   python rag.py
   ```
   ※ 質問文やインデックス名は、必要に応じて変更してください。

5. **Elasticsearch 接続テスト**  
   Elasticsearch の接続確認や簡単な検索テストを実施する場合は、以下を実行します。
   ```bash
   python scripts/es_test.py
   ```

6. **MSD記事のスクレイピング**  
   MSDのWeb記事をスクレイピングする場合は、`scripts/msd.py` 内の `BASE_URL` 等を必要に応じて設定した上で、以下を実行します。
   ```bash
   python scripts/msd.py
   ```
   スクレイピングしたデータは、指定されたJSONファイルに保存されます。

## LangChain と Elasticsearch について

### LangChain
[LangChain](https://github.com/hwchase17/langchain) は、大規模言語モデル（LLM）を活用したアプリケーションの構築を支援するフレームワークです。  
- **チェーン（Chains）**: LLMの呼び出し、文書検索、データ処理などを組み合わせたパイプラインを構築できます。  
- **埋め込みとベクトルストア**: 文書の埋め込み生成および、Elasticsearchなどのベクトルデータベースとの連携が可能です。  

### Elasticsearch
[Elasticsearch](https://www.elastic.co/elasticsearch/) は、高速でスケーラブルな全文検索エンジンです。  
- **インデックス作成**: 文書（またはそのチャンク）をインデックスに格納し、検索を高速に実施します。  
- **セマンティック検索**: 埋め込みベクトルを利用した類似度検索により、意味的に近い文書を効率的に検索できます。  
- **セキュリティ**: CA証明書やフィンガープリントなどの設定により、安全な接続が可能です。
