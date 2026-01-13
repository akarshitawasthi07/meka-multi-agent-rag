import os
from langchain_community.document_loaders import (
    TextLoader, 
    PyPDFLoader, 
    Docx2txtLoader, 
    CSVLoader, 
    JSONLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_documents(data_path="data"):
    """
    Loads documents from the data directory supporting multiple formats.
    """
    docs = []
    if not os.path.exists(data_path):
        os.makedirs(data_path)
        return docs

    for file in os.listdir(data_path):
        file_path = os.path.join(data_path, file)
        try:
            if file.endswith(".txt"):
                loader = TextLoader(file_path, encoding="utf-8")
                docs.extend(loader.load())
            elif file.endswith(".pdf"):
                loader = PyPDFLoader(file_path)
                docs.extend(loader.load())
            elif file.endswith(".docx"):
                loader = Docx2txtLoader(file_path)
                docs.extend(loader.load())
            elif file.endswith(".csv"):
                loader = CSVLoader(file_path)
                docs.extend(loader.load())
            elif file.endswith(".json"):
                # For JSON, we use a simple schema. If more complex, jq_schema may be needed.
                loader = JSONLoader(file_path, jq_schema='.[]', text_content=False)
                docs.extend(loader.load())
        except Exception as e:
            print(f"Error loading {file}: {e}")

    return docs

def get_chunks(documents):
    """
    Splits documents into smaller chunks for better RAG performance.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        add_start_index=True
    )
    return text_splitter.split_documents(documents)