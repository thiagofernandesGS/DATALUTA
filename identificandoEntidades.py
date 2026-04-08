# 1. Importações
import json
import spacy
from spacy.matcher import PhraseMatcher
import re
from bs4 import BeautifulSoup

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
                bioma = [
                    cidade.get("BiomaP"),
                    cidade.get("BiomaS"),
                    cidade.get("BiomaT")
                ]
                bioma = "; ".join([b for b in bioma if b])

                results.append({
                    "tipo": "cidade",
                    "nome": termo,
                    "frase": frase,
                    "estado": estado["name"],
                    "sigla": estado["sigla"],
                    "regiao": regiao_nome,
                    "cidade_id": cidade["id"],
                    "bioma": bioma
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
"""
def extrair_info_llm(resposta):
    if "Local não identificado" in resposta:
        return None

    escala = None
    local = None
    estado = None
    regiao = None
    codigo_ibge = None
    bioma = None

    for linha in resposta.split("\n"):
        if "Escala:" in linha:
            escala = linha.split("Escala:")[1].strip()

        elif "Local:" in linha:
            local = linha.split("Local:")[1].strip()

        elif "Estado:" in linha:
            estado = linha.split("Estado:")[1].strip()

        elif "Região:" in linha:
            regiao = linha.split("Região:")[1].strip()

    if escala == "Municipal" and local:
        for nome_cidade, cidade in cities.items():
            if nome_cidade.lower() == local.lower():

                estado_id = str(cidade["state_id"])
                estado_info = states.get(estado_id)

                codigo_ibge = cidade.get("id")

                biomas = [
                    cidade.get("BiomaP"),
                    cidade.get("BiomaS"),
                    cidade.get("BiomaT")
                ]
                bioma = ", ".join([b for b in biomas if b])

                estado = estado_info["name"]
                regiao = regions.get(estado_id[0])

                break

    elif escala == "Estadual" and estado:
        for eid, est in states.items():
            if est["sigla"].lower() == estado.lower() or est["name"].lower() == local.lower():

                codigo_ibge = eid
                regiao = regions.get(eid[0])
                estado = est["sigla"]

                break

    elif escala == "Nacional":
        return ("Nacional", "Brasil", None, "Brasil", None, None)

    return escala, local, estado, regiao, codigo_ibge, bioma
"""

"""
def extrair_informacao_planilha(resposta):
    info = None
    if resposta[0] == "Municipal":
        info = f"{resposta[3]} ; {resposta[2]} ; {resposta[1]}; {resposta[4]}"
        escala = resposta[0]
        bioma = resposta[5]
        return info, escala, bioma
    elif resposta[0] == "Estadual":
        info = f"{resposta[0]} ; {resposta[1]} ; {resposta[4]}"
        escala = resposta[0]
        return info, escala
    escala = "Nacional"
    return escala, info
"""
"""
def extrair_info_llm(resposta):
    if "Local não identificado" in resposta:
        return None

    escala = None
    local = None
    estado = None
    regiao = None
    codigo_ibge = None
    bioma = None

    for linha in resposta.split("\n"):
        if "Escala:" in linha:
            escala = linha.split("Escala:")[1].strip()

        elif "Local:" in linha:
            local = linha.split("Local:")[1].strip()

        elif "Estado:" in linha:
            estado = linha.split("Estado:")[1].strip()

        elif "Região:" in linha:
            regiao = linha.split("Região:")[1].strip()

    if local:
        for nome_cidade, cidade in cities.items():
            if nome_cidade.lower() == local.lower():

                estado_id = str(cidade["state_id"])
                estado_info = states.get(estado_id)


                codigo_ibge = cidade.get("id")

                biomas = [
                    cidade.get("BiomaP"),
                    cidade.get("BiomaS"),
                    cidade.get("BiomaT")
                ]
                bioma = ", ".join([b for b in biomas if b])

                estado = estado_info["name"]
                regiao = regions.get(estado_id[0])

                return escala, local, estado, regiao, codigo_ibge, bioma

    if estado:
        for eid, est in states.items():
            if est["sigla"].lower() == estado.lower() or est["name"].lower() == estado.lower():

                codigo_ibge = eid
                regiao = regions.get(eid[0])
                estado = est["name"]

                return escala, None, estado, regiao, codigo_ibge, None

    if escala == "Nacional":
        return ("Nacional", None, "Nacional", "Nacional", None, None)

    return escala, local, estado, regiao, codigo_ibge, bioma
"""

def extrair_info_llm(resposta):
    if "Local não identificado" in resposta:
        return None

    escala = None
    local = None
    estado = None
    regiao = None

    for linha in resposta.split("\n"):
        if "Escala:" in linha:
            escala = linha.split("Escala:")[1].strip()

        elif "Local:" in linha:
            local = linha.split("Local:")[1].strip()

        elif "Estado:" in linha:
            estado = linha.split("Estado:")[1].strip()

        elif "Região:" in linha:
            regiao = linha.split("Região:")[1].strip()

    estado_info = None
    if estado:
        for eid, est in states.items():
            if est["sigla"].lower() == estado.lower() or est["name"].lower() == estado.lower():
                estado_info = (eid, est)
                break

    if local:
        for nome_cidade, cidade in cities.items():
            if nome_cidade.lower() == local.lower():

                estado_id = str(cidade["state_id"])
                est = states.get(estado_id)

                if estado_info:
                    if estado_id != estado_info[0]:
                        continue

                elif escala == "Estadual":
                    continue  # evita pegar cidade quando deveria ser estado

                biomas = [
                    cidade.get("BiomaP"),
                    cidade.get("BiomaS"),
                    cidade.get("BiomaT")
                ]
                bioma = ", ".join([b for b in biomas if b])

                return (
                    escala,
                    nome_cidade,
                    est["name"],
                    regions.get(estado_id[0]),
                    cidade.get("id"),
                    bioma
                )

    if estado_info:
        eid, est = estado_info
        return (
            escala,
            None,
            est["name"],
            regions.get(eid[0]),
            eid,
            None
        )

    if local:
        # decide pela escala
        if escala == "Municipal":
            for nome_cidade, cidade in cities.items():
                if nome_cidade.lower() == local.lower():
                    estado_id = str(cidade["state_id"])
                    est = states.get(estado_id)

                    return (
                        escala,
                        nome_cidade,
                        est["name"],
                        regions.get(estado_id[0]),
                        cidade.get("id"),
                        None
                    )

        elif escala == "Estadual":
            for eid, est in states.items():
                if est["name"].lower() == local.lower():
                    return (
                        escala,
                        None,
                        est["name"],
                        regions.get(eid[0]),
                        eid,
                        None
                    )

    if escala == "Nacional":
        return ("Nacional", None, "Nacional", None, None, None)

    return escala, local, estado, regiao, None, None

def extrair_informacao_planilha(resposta):
    #print(resposta)
    if resposta is None:
        return None, None, None

    escala, local, estado, regiao, codigo, bioma = resposta

    partes = []

    if regiao:
        partes.append(regiao)

    if estado:
        partes.append(estado)

    if local:
        partes.append(local)

    if codigo:
        partes.append(str(codigo))

    info = " ; ".join(partes) if partes else "NI"

    # ---------------- BIOMA ---------------- #
    if not bioma:
        bioma = "NI"

    # ---------------- ESCALA ---------------- #
    if not escala:
        escala = "NI"

    return info, escala, bioma

#funcao do Yan
def extrair_texto(texto):
    source = texto.text  # biblioteca requests
    html = re.search(r"<html\b[^>]*>.*?</html>", source, flags=re.DOTALL | re.IGNORECASE).group()
    html2 = re.sub(r'<style.*?>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
    html3 = re.sub(r'<script.*?>.*?</script>', '', html2, flags=re.DOTALL | re.IGNORECASE)
    html4 = re.sub(r'<link.*?rel=["\']stylesheet["\'][^>]*>', '', html3, flags=re.IGNORECASE)
    html5 = re.sub(r'<script.*?src=["\'][^"\']+["\'][^>]*>', '', html4, flags=re.IGNORECASE)
    filtro = BeautifulSoup(html5, 'html.parser')
    texto_limpo = filtro.get_text(separator=' ', strip=True)
    return texto_limpo


