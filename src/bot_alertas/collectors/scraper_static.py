"""
Coletor genérico para páginas estáticas (scraping simples).

Percorre todas as fontes definidas em `config.STATIC_SOURCES` e extrai
links cujo texto contenha a palavra "edital".

Ideal para sites que não oferecem RSS e têm estrutura simples de links.
Para sites com proteção anti-bot ou estrutura complexa, prefira criar
um coletor específico (como observatorio_terceiro_setor.py).

Para adicionar novas fontes, edite `src/bot_alertas/config.py`:

    STATIC_SOURCES = {
        "Nome da Fonte": "https://url-da-pagina.com.br/editais",
    }
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime

from ..config import STATIC_SOURCES

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def coletar_static() -> list[dict]:
    """
    Coleta links de editais a partir de páginas HTML estáticas.

    Busca qualquer link (<a>) cujo texto visível contenha "edital".
    A data de publicação é definida como hoje (não é possível inferir
    sem acesso ao detalhe de cada página).

    Returns:
        Lista de dicts com os campos:
          - fonte (str)
          - titulo (str)
          - resumo (str, vazio)
          - link (str)
          - data (str, formato DD/MM/YYYY)
    """
    resultados = []
    hoje = datetime.now().strftime("%d/%m/%Y")

    for fonte, url in STATIC_SOURCES.items():
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "lxml")
            links = soup.find_all("a")

            for link_tag in links:
                titulo = link_tag.get_text(strip=True)
                href = link_tag.get("href")

                if not titulo or not href:
                    continue

                if "edital" not in titulo.lower():
                    continue

                # Garante que o link seja absoluto
                if not href.startswith("http"):
                    href = url.rstrip("/") + "/" + href.lstrip("/")

                resultados.append({
                    "fonte": fonte,
                    "titulo": titulo,
                    "resumo": "",
                    "link": href,
                    "data": hoje,
                })

        except Exception as e:
            print(f"  ⚠ Erro ao coletar fonte estática '{fonte}': {e}")

    return resultados
