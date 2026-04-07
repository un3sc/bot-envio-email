"""
Coletor de editais do Diário Oficial da União (DOU).

Realiza buscas na API pública do DOU (in.gov.br) filtrando
por artigos do tipo "Edital" publicados nos últimos 30 dias.

Documentação da API: https://www.in.gov.br/consulta

ATENÇÃO: O DOU retorna um volume muito grande de editais.
Sem um pré-filtro adequado, o custo de tokens do Gemini pode ser alto.
Recomenda-se usar este coletor em conjunto com o pré-filtro regex
(`passa_pre_filtro` em filter.py) antes de enviar ao Gemini.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

BASE_URL = "https://www.in.gov.br/consulta/-/buscar/dou"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0 Safari/537.36"
    )
}

# Janela de busca: publicações dos últimos N dias
JANELA_DIAS = 30
PAGE_SIZE = 20


def coletar_dou() -> list[dict]:
    """
    Coleta editais publicados recentemente no Diário Oficial da União.

    Returns:
        Lista de dicts com os campos:
          - fonte (str)
          - titulo (str)
          - resumo (str, vazio — conteúdo completo está na URL)
          - link (str)
          - data (str, formato DD/MM/YYYY)
    """
    resultados = []
    hoje = datetime.now()
    data_inicio = (hoje - timedelta(days=JANELA_DIAS)).strftime("%d/%m/%Y")
    data_fim = hoje.strftime("%d/%m/%Y")

    start = 0

    while True:
        url = (
            f"{BASE_URL}"
            f"?q=*"
            f"&s=todos"
            f"&exactDate=personalizado"
            f"&sortType=0"
            f"&delta={PAGE_SIZE}"
            f"&start={start}"
            f"&publishFrom={data_inicio}"
            f"&publishTo={data_fim}"
            f"&artType=Edital"
        )

        try:
            response = requests.get(url, headers=HEADERS, timeout=20)
            response.raise_for_status()
        except Exception as e:
            print(f"  ⚠ Erro ao coletar DOU (start={start}): {e}")
            break

        soup = BeautifulSoup(response.text, "lxml")
        itens = soup.find_all("h5", class_="title-marker")

        if not itens:
            break  # Sem mais resultados

        for item in itens:
            link_tag = item.find("a")
            if not link_tag:
                continue

            titulo = link_tag.get_text(strip=True)
            link = "https://www.in.gov.br" + link_tag["href"]

            resultados.append({
                "fonte": "Diário Oficial da União",
                "titulo": titulo,
                "resumo": "",
                "link": link,
                "data": hoje.strftime("%d/%m/%Y"),
            })

        print(f"  ✔ DOU: {len(itens)} item(ns) coletado(s) (start={start})")
        start += PAGE_SIZE

    return resultados
