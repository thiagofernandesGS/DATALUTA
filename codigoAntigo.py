import json
import spacy
from spacy.pipeline import EntityRuler

# 1. Carrega o JSON
with open("dadosAntigos.json", encoding="utf-8") as f:
    dados = json.load(f)

# 2. Cria dicionários auxiliares
id_estado_para_nome = dados["states"]  # id (str) → nome
id_regiao_para_nome = dados["regions"]  # id (str) → nome
cidade_para_info = {}  # nome da cidade → info

for cidade in dados["cities"]:
    id_estado_str = str(cidade["state_id"])
    id_regiao_str = id_estado_str[0]
    nome_estado = id_estado_para_nome.get(id_estado_str, "Desconhecido") #se o ID não for encontrado no dicionário, retorna "Desconhecido"
    nome_regiao = id_regiao_para_nome.get(id_regiao_str, "Desconhecido") #se o ID não for encontrado no dicionário, retorna "Desconhecido"
    cidade_para_info[cidade["name"]] = {
        "cidade_id": cidade["id"],
        "bioma_principal": cidade.get("biomaP"),
        "bioma_secundario": cidade.get("biomaS"),
        "bioma_terciario": cidade.get("biomaT"),
        "estado_id": id_estado_str,
        "estado_nome": nome_estado,
        "regiao_nome": nome_regiao,
    }

# 3. Configura spaCy com o EntityRuler
nlp = spacy.load("pt_core_news_lg")
ruler = nlp.add_pipe("entity_ruler", before="ner")

# 4. Adiciona padrões com os nomes das cidades
padroes = [{"label": "LOC", "pattern": nome} for nome in cidade_para_info]
ruler.add_patterns(padroes)

# 5. Texto de entrada
texto = ("A Prefeitura de Campo Grande por meio da Secretaria Municipal de Assistência Social (SAS), em parceria com a Fundação Nacional do Índio (Funai), está realizando a entrega emergencial de 230 cestas básicas para a população indígena de três comunidades localizadas no Jardim Noroeste. O objetivo é garantir a segurança alimentar das famílias devido à pandemia. A distribuição acontece até esta terça-feira (31) nas comunidades Água Funda, Estrela do Amanhã e Nova Canaã.")
doc = nlp(texto)

# 6. Verifica as entidades e exibe resultados
for ent in doc.ents:
    if ent.label_ == "LOC":
        info = cidade_para_info.get(ent.text)
        if info:
            print(f"{ent.text} → Região: {info['regiao_nome']}, Estado: {info['estado_nome']}, Cidade ID: {info['cidade_id']}, Bioma Principal: {info['bioma_principal']}, Bioma Secundario: {info['bioma_secundario']}, Bioma Terciario: {info['bioma_terciario']}")
        else:
            print(f"{ent.text} → Informação não encontrada")