# 1. Importações
import json
import spacy
from spacy.pipeline import EntityRuler

# 2. Carrega o JSON
with open("dados.json", encoding="utf-8") as f:
    dados = json.load(f)

# 3. Criação de dicionários com os dados gerais
nomes_cidades = list(dados["cities"].keys())
states = dados["states"]
regions = dados["regions"]
cities = dados["cities"]

# 3. Configura o spaCy e adiciona o EntityRuler
nlp = spacy.load("pt_core_news_lg")
ruler = nlp.add_pipe("entity_ruler", before="ner")

# 4. Adiciona padrões de cidades
padroes = [{"label": "LOC", "pattern": nome} for nome in nomes_cidades]
ruler.add_patterns(padroes)


def encontrar_locais(texto):
    # 5. Verifica as entidades e exibe resultados
    doc = nlp(texto)
    for ent in doc.ents:
        if ent.label_ == "LOC":
            cidade_info = cities.get(ent.text)
            if cidade_info:
                estado_id = str(cidade_info["state_id"])
                estado_info = states.get(estado_id, {})
                regiao_id = estado_id[0]
                regiao_nome = regions.get(regiao_id, "Desconhecido")
                print(f"{ent.text} → Região: {regiao_nome}, Estado: {estado_info.get('name', 'Desconhecido')}, Sigla do Estado: {estado_info.get('sigla', 'Desconhecido')}, Cidade ID: {cidade_info['id']}, Bioma Principal: {cidade_info.get('BiomaP', 'Desconhecido')}, Bioma Secundário: {cidade_info.get('BiomaS', 'Não contêm')}, Bioma Terciário: {cidade_info.get('BiomaT', 'Não contêm')}")
            else:
                print(f"{ent.text} → Informação não encontrada")

