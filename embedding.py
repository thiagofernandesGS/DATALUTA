import os

from langchain_core.vectorstores import InMemoryVectorStore
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from langchain_core.documents import Document

nvidia_key = os.getenv("NVIDIA_API_KEY")

def criar_vector_store(result):
    # Inicializa embeddings NVIDIA
    embeddings = NVIDIAEmbeddings(model="nvidia/nv-embed-v1")

    # Cria vetor store em memória
    vector_store = InMemoryVectorStore(embeddings)

    # Converte nossas frases em documentos langchain
    print("Convertendo frases...")

    docs = []
    for data in result:
        #print(f"frase = {data['frase']}, escala = {data['tipo']}, regiao = {data['regiao']}")
        content = data['frase']
        metadata = {"escala": data["tipo"], "regiao": data["regiao"]}
        docs.append(Document(page_content=content, metadata=metadata))

    print("frases convertidas.")

    # Adiciona documentos ao vector store
    print("Adicionando documentos no vector store")
    vector_store.add_documents(docs)
    print("documentos adicionados")
    return vector_store
