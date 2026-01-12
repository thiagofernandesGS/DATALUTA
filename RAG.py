import os

from langchain.chat_models import init_chat_model
from identificandoEntidades import encontrar_locais
from embedding import criar_vector_store

# Carrega API Keys do ambiente
langsmith_key = os.getenv("LANGSMITH_API_KEY")

# Inicializa LLM NVIDIA
llm = init_chat_model(
    "meta/llama-3.1-70b-instruct",
    model_provider="nvidia"
)

def generate(vector_store, noticia):
    retrieved_docs = vector_store.similarity_search(noticia, k=5)

    context_text = "\n\n".join(
        [
            f"Frase: {doc.page_content}\n Escala: {doc.metadata['escala']} Região: {doc.metadata['regiao']}\n"
            for doc in retrieved_docs
        ]
    )
    #print("context_text = ", context_text)

    prompt = f"""
    A seguir estão frases extraídas contendo localidades identificadas no texto:

    {context_text}

    Agora responda:

    Dada a notícia abaixo, diga QUAL LOCAL (cidade, estado ou região) é o mais provável onde a notícia ocorreu.

    Notícia: {noticia}

    Responda somente no formato:

    Escala: <Municipal|Estadual|Regional|Nacional>
    Local: <nome>
    Estado: <sigla ou vazio>
    Região: <nome>

    Se não conseguir identificar, responda exatamente:
    Local não identificado
    """

    response = llm.invoke(prompt)
    return response.content
