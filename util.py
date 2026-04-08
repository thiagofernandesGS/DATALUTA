from datetime import datetime
import string
import pandas as pd
import os

def gerar_codigo(indice):
    hoje = datetime.now().strftime("%d%m%y")

    letras = string.ascii_uppercase

    if indice < 26:
        sufixo = letras[indice]
    else:
        sufixo = letras[indice // 26 - 1] + letras[indice % 26]

    return f"FLO{hoje}{sufixo}"

def adiciona_planilha(arquivo, resultados):

    df_novo = pd.DataFrame(
        resultados,
        columns=[
            "Data da notícia",
            "Código da notícia",
            "Título da notícia",
            "Fonte da notícia",
            "Macrorregião, Estado, Município e código",
            "Escala da ação",
            "Bioma"
        ]
    )

    if os.path.exists(arquivo):
        df_antigo = pd.read_excel(arquivo)
        df_final = pd.concat([df_antigo, df_novo], ignore_index=True)
    else:
        df_final = df_novo

    df_final.to_excel(arquivo, index=False)

    print("Dados adicionados na planilha com sucesso!")