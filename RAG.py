import os

from langchain.chat_models import init_chat_model
from identificandoEntidades import encontrar_locais
from embedding import criar_vector_store
from langchain_text_splitters import RecursiveCharacterTextSplitter
import time

# Carrega API Keys do ambiente
langsmith_key = os.getenv("LANGSMITH_API_KEY")
nvidia_key = os.getenv("NVIDIA_API_KEY")
#print(nvidia_key)

# Inicializa LLM NVIDIA
llm = init_chat_model(
    "meta/llama-3.1-70b-instruct",
    model_provider="nvidia",
    api_key = nvidia_key
)


def generate(vector_store, noticia):
    # 1. Dividir a notícia em pedaços que cabem no modelo (limite 512 tokens)
    # Usamos 1000 caracteres para ter uma margem de segurança
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    chunks = text_splitter.split_text(noticia)

    all_retrieved_docs = []

    # 2. Buscar contexto para os primeiros pedaços (ou os mais importantes)
    # Geralmente os primeiros parágrafos contêm a localização principal
    for chunk in chunks[:3]:
        docs = vector_store.similarity_search(chunk, k=2)
        all_retrieved_docs.extend(docs)

    # Remover duplicatas se houver
    unique_docs = {doc.page_content: doc for doc in all_retrieved_docs}.values()
    # 3. Montar o contexto
    context_text = "\n\n".join(
        [
            f"Frase: {doc.page_content}\nEscala: {doc.metadata['escala']} Região: {doc.metadata['regiao']}"
            for doc in unique_docs
        ]
    )

    #print("melhores frases: ", context_text)
    #print("noticia: ", noticia)
    # 5. Criar prompt
    prompt = f"""
Você é um especialista em Geolinguística e Processamento de Linguagem Natural (NLP), focado na análise de notícias brasileiras.

### Objetivo
Identificar com precisão geográfica o LOCAL PRINCIPAL onde o fato narrado ocorreu, distinguindo-o de menções secundárias ou nomes próprios.

### Processo de Análise
1. Identifique o evento central da notícia.
2. Localize onde esse evento ocorreu (Ex: Se a notícia é sobre uma enchente em Gramado, o local é Gramado, mesmo que a notícia tenha sido escrita em Porto Alegre).
3. Verifique se o termo geográfico não é, na verdade, um sobrenome ou nome de instituição.
4. Determine a escala de abrangência do impacto do fato, sendo eles Municipal|Estadual|Regional|Nacional.

### Regras de Ouro
- **Prioridade:** O local do evento > Local da publicação.
- **Escala:** A Escala se dá em quanto a notícia afeta, se ela afeta o municipio, Municipal; Estado -> Estadual; Região -> Regional; País -> Nacional.
- **Incerteza:** Se o texto não citar cidade ou estado, e não for claramente nacional, responda "Local não identificado".

### Dados para Processamento
Frases de Apoio: 
{context_text}

Conteúdo da Notícia: 

{noticia}


### Resposta (Siga estritamente este formato):
Escala: <Municipal|Estadual|Regional|Nacional>
Local: <nome ou vazio>
Estado: <nome completo ou vazio>
Região: <nome ou vazio>
    """

    time.sleep(25)
    response = llm.invoke(prompt)
    return response.content
