def load_documents():
    """
    Returns raw documents (not chunks)
    Used by BM25 keyword retriever
    """
    from langchain_community.document_loaders import TextLoader
    import os

    docs = []
    data_path = "data"

    for file in os.listdir(data_path):
        if file.endswith(".txt"):
            loader = TextLoader(os.path.join(data_path, file), encoding="utf-8")
            docs.extend(loader.load())

    return docs