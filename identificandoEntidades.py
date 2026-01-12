# 1. Importações
import json
import spacy
from spacy.matcher import PhraseMatcher

# 2. Carrega o JSON
with open("dados.json", encoding="utf-8") as f:
    dados = json.load(f)

# 3. Criação de dicionários com os dados gerais
states = dados["states"]
regions = dados["regions"]
cities = dados["cities"]

# 4. Lista de Matchers (com cidade, estados/siglas e regiões)
nomes_cidades = list(cities.keys())
nomes_estados = [v["name"] for v in states.values()]
siglas_estados = [v["sigla"] for v in states.values()]
nomes_regioes = list(regions.values())

# 5. Configura o spaCy e cria matcher
nlp = spacy.load("pt_core_news_lg")
matcher = PhraseMatcher(nlp.vocab, attr="LOWER")

# 6. Cria os padrões que queremos buscar
patterns_cidades = [nlp.make_doc(nome) for nome in nomes_cidades]
patterns_estados = [nlp.make_doc(nome) for nome in nomes_estados]
patterns_siglas = [nlp.make_doc(sigla) for sigla in siglas_estados]
patterns_regioes = [nlp.make_doc(nome) for nome in nomes_regioes]

matcher.add("CIDADE", patterns_cidades)
matcher.add("ESTADO", patterns_estados)
matcher.add("ESTADO_SIGLA", patterns_siglas)
matcher.add("REGIAO", patterns_regioes)



# 7. Texto a ser analisado está na variavel "texto"
def encontrar_locais(texto):
    results = []
    # 8. Verifica as entidades e exibe resultados
    doc = nlp(texto)
    matches = matcher(doc)

    for match_id, start, end in matches:
        label = nlp.vocab.strings[match_id]
        termo = doc[start:end].text
        frase = doc[start:end].sent.text

        if label == "CIDADE":
            cidade = cities.get(termo)
            if cidade:
                estado_id = str(cidade["state_id"])
                estado = states.get(estado_id)
                regiao_nome = regions.get(estado_id[0])

                results.append({
                    "tipo": "cidade",
                    "nome": termo,
                    "frase": frase,
                    "estado": estado["name"],
                    "sigla": estado["sigla"],
                    "regiao": regiao_nome,
                    "cidade_id": cidade["id"]
                })

        elif label == "ESTADO":
            estado = next((s for s in states.values() if s["name"] == termo), None)
            if estado:
                estado_id = next((eid for eid, s in states.items() if s is estado), None)
                regiao_nome = regions.get(estado_id[0])

                results.append({
                    "tipo": "estado",
                    "nome": estado["name"],
                    "sigla": estado["sigla"],
                    "frase": frase,
                    "regiao": regiao_nome,
                    "estado_id": estado_id
                })

        elif label == "ESTADO_SIGLA":
            estado = next((s for s in states.values() if s["sigla"].lower() == termo.lower()), None)
            if estado:
                estado_id = next((eid for eid, s in states.items() if s is estado), None)
                regiao_nome = regions.get(estado_id[0])

                results.append({
                    "tipo": "estado",
                    "nome": estado["name"],
                    "sigla": estado["sigla"],
                    "frase": frase,
                    "regiao": regiao_nome
                })

        elif label == "REGIAO":
            regiao_id = next((rid for rid, nome in regions.items() if nome == termo), None)
            results.append({
                "tipo": "regiao",
                "nome": termo,
                "frase": frase,
                "regiao": regiao_id
            })

    results = limpar_duplicadas(results)
    return results

def limpar_duplicadas(results):
    vistos = set()
    unicos = []
    for loc in results:
        chave = (loc["frase"], loc["tipo"])
        if chave not in vistos:
            vistos.add(chave)
            unicos.append(loc)
    return unicos
