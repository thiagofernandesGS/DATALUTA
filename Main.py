# install bs4, spacy, pandas, pt_core_news_lg(sm), openpyxl
#python -m spacy download pt_core_news_lg


import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import pandas as pd
import identificandoEntidades
from embedding import criar_vector_store
from RAG import generate
import sys


# ---------------------------------------------------------------------------Funções----------------------------------------------------------------------------------#
# 1 Funções para a raspagem das informações (principalmente data)
# 1.1 Função para extrair o dominio
def extrair_dominio(url):
    parsed_url = urlparse(url)
    # Pega o domínio (sem www, por exemplo)
    dominio = parsed_url.netloc
    return dominio


# 1.2 Função para extrair a data de um site WordPress
def IsWordpress(Formatacao):
    data = Formatacao.find("meta", {'property': ['article:published_time', 'og:updated_time']})

    # Se a tag for encontrada conseguimos coletar a data
    if data and 'content' in data.attrs:
        data_publicacao = data.attrs['content']
        data_sem_hora = data_publicacao.split('T')[0]
        ano, mes, dia = data_sem_hora.split('-')

        # Inverte para o formato DD-MM-YYYY
        data_invertida = f"{dia}-{mes}-{ano}"
        return data_invertida

    return "nao entrado Wordpress"


# 1.3 Função para extrair a data quando ela se encontra na tag "time"
def DataTime(Formatacao):
    # Encontra a tag <time>
    time = Formatacao.find("time")
    datetime_value = time.get("datetime")  # Pega o valor do atributo datetime
    if datetime_value and datetime_value != "#":
        data = datetime_value  # Se o datetime for válido, usa ele
    else:
        data = time.text.strip()  # Pega o texto dentro da tag <time>

    return data


# 1.4 Função para extrair a data quando ela se encontra na tag "meta" no campo "article"
def Meta(Formatacao):
    meta_tag = Formatacao.find("meta", {'property': ['og:article:published_time', 'article:published_time']})

    if meta_tag and 'content' in meta_tag.attrs:
        # Extrai a data do atributo 'content' e formata
        data_publicacao = meta_tag['content']
        data_sem_hora = data_publicacao.split('T')[0]
        data_sem_espaço = data_sem_hora.split(' ')[0]
        ano, mes, dia = data_sem_espaço.split('-')

        # Formata para o formato DD-MM-YYYY
        data_invertida = f"{dia}-{mes}-{ano}"
        return data_invertida

    return "Não encontrado meta"


# 1.5 Função para extrairr a data quando ela se encontra na tag "div" na class "ms-1"
def Divms(Formatacao):
    data_divs = Formatacao.find_all("div",
                                    class_="ms-1")  # pega todas as divs com a classe "ms-1", no caso da agencia Para, duas.

    # a função next procura todos os elementos da nossa lista, neste caso ela percorre todas as divs com class="ms-1"
    # contém uma data (procurando a barra '/' ou '-')
    data_div = next((div for div in data_divs if div.text and ("/" in div.text or "-" in div.text)), None)

    # Se encontrou, extrai o texto e remove espaços extras
    data = data_div.text.strip() if data_div else None
    return data


# 1.6 Função para extriar a data quando ela se encontra na tag "div" na class "AutorDataPublicacao"
def DivAutor(Formatacao):
    data_texto = Formatacao.find("div", class_="AutorDataPublicacao")
    data_texto = data_texto.text.strip()
    data = data_texto.split(" | ")[1]
    return data


# 1.7 Função para extrair a data quando ela se encontra na tag "div" na class "news-publishinfo"
def DivNews(Formatacao):
    data_texto = Formatacao.find("div", class_="news-publishinfo")
    data = data_texto.find("p").text.strip()
    return data


# 1.8 Função para extrair a data quando ela se encontra na tag "span"
def DataSpan(Formatacao):
    data_texto = Formatacao.find("span")
    data = data_texto.text.strip()
    return data


# 1.9 Sites onde o titulo está na tag titulo ou está separado pelo caractere |
def Ocorrencia1(site, linha):
    Formatacao = BeautifulSoup(site.text, 'html.parser')
    titulo = Formatacao.title.string
    titulof = titulo.split("|")[0]
    local = None
    parsed_url = urlparse(linha)
    dominio = parsed_url.netloc

    if 'wp-content' in Formatacao.prettify() or 'wp-admin' in Formatacao.prettify():
        data = IsWordpress(Formatacao)

    elif Formatacao.find("meta", {
        'property': ['og:article:published_time', 'article:published_time', 'article:modified_time']}):
        data = Meta(Formatacao)

    elif Formatacao.find("time"):
        data = DataTime(Formatacao)

    elif Formatacao.find("div", class_="ms-1"):
        data = Divms(Formatacao)

    else:
        data = None

    return [titulof, dominio, local, data]


# 1.10 Sites onde o titulo está na tag titulo ou está separado pelo caractere -
def Ocorrencia2(site, linha):
    Formatacao = BeautifulSoup(site.text, 'html.parser')
    titulo = Formatacao.title.string
    titulof = titulo.split('–')[0]
    parsed_url = urlparse(linha)
    dominio = parsed_url.netloc

    if 'wp-content' in Formatacao.prettify() or 'wp-admin' in Formatacao.prettify():
        data = IsWordpress(Formatacao)

    elif Formatacao.find("meta", {'property': ['og:article:published_time', 'article:published_time']}):
        data = Meta(Formatacao)

    elif Formatacao.find("time"):
        data = DataTime(Formatacao)

    elif Formatacao.find("div", class_="AutorDataPublicacao"):
        data = DivAutor(Formatacao)

    elif Formatacao.find("div", class_="news-publishinfo"):
        data = DivNews(Formatacao)

    else:
        data = None

    local = None
    return [titulof, dominio, local, data]


# ---------------------------------------------------------------------------MAIN----------------------------------------------------------------------------------#

# 2.1 listas dos sites que conseguimos fazer a extração
Lista1 = ["cimi.org.br", "g1.globo.com", "brasildefato.com.br", "agenciabrasil.ebc.com.br", "metropoles.com",
          "midiamax.uol.com.br", "tvt.org.br", "socioambiental.org", "jornalistaslivres.org", "agenciapara.com.br",
          "gazetadocerrado.com.br",
          "revistaforum.com.br", "uol.com.br", "oglobo.globo.com", "gov.br", "terra.com.br", "tapajósdefato.com.br",
          "correiobraziliense.com.br",
          "opovo.com.br", "agenciacenarium.com.br", "noticias.uol.com.br", "gov.br/pt-br", "correiodopovo.com.br",
          "funai.gov.br", "acritica.uol.com.br", "ndmais.com.br", "revistacenarium.com.br", "f5.folha.uol.com.br",
          "acritica.net"]

Lista2 = ["seculodiario.com.br", "amazoniareal.com.br", "campograndenews.com.br", "folha.uol.com.br",
          "anovademocracia.com.br",
          "ihu.unisinos.br", "conexaoto.com.br", "combateracismoambiental.net.br", "folhabv.com.br", "sul21.com.br",
          "cartacapital.com.br", "oeco.org.br", "folhabv.com.br", "racismoambiental.net.br", "em.com.br"]

resultados = []

# 2.2 Lendo os link do arquivo e fazendo request para "enganar" o site
with open("links.txt", 'r') as file:
    for linha in file:
        linha = linha.strip()
        response = requests.get(linha,
                                headers={
                                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'},
                                timeout=105)
        # url, paprams, headers, cookies, auth, timeout, allow_redirects

        # 2.3 Extrai o domínio da URL
        dominio_extraido = extrair_dominio(linha).replace("www.", "").replace("www1.", "")

        if response.status_code == 200:
            response.encoding = 'utf-8'


            texto = BeautifulSoup(response.text, 'html.parser').get_text(separator=' ', strip=True)

            # 2.4 Procura as entidades nomeadas do texto e utiliza RAG para acuracia.
            locais_encontrados = identificandoEntidades.encontrar_locais(texto)
            print(locais_encontrados)
            frases_locais = criar_vector_store(locais_encontrados)
            encontrar_local = generate(frases_locais, texto)
            print(encontrar_local)
            print("-" * 75)




            # 2.5 coletando as informaões dos sites
            if dominio_extraido in Lista1:
                resultado = Ocorrencia1(response, linha)
                #print(resultado)
                resultados.append(resultado)

            elif dominio_extraido in Lista2:
                resultado = Ocorrencia2(response, linha)
                #print(resultado)
                resultados.append(resultado)

            else:
                print("")
                print("------")
                print("nao encontrado na base de dados")
                print(linha)
                print(dominio_extraido)
                print("------")

# 2.6 Criado uma planilha com as informações coletadas
df = pd.DataFrame(resultados, columns=["Título", "Mídia", "Local", "Data"])

# Exportando para um arquivo Excel
df.to_excel("resultados.xlsx", index=False)

print("Resultados exportados para resultados.xlsx")
