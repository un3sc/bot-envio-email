"""
Coletor de editais do Observatório do Terceiro Setor.

Faz scraping da página de editais usando cloudscraper (contorna
proteções anti-bot básicas do Cloudflare) e retorna artigos
publicados nos últimos 30 dias.

Fonte: https://observatorio3setor.org.br/secoes_tematicas/editais/
"""

import cloudscraper
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

URL = "https://observatorio3setor.org.br/secoes_tematicas/editais/"
FONTE = "Observatório do Terceiro Setor"

# Janela de busca: considera publicações dos últimos N dias
JANELA_DIAS = 30


def coletar() -> list[dict]:
    """
    Coleta editais publicados recentemente no Observatório do Terceiro Setor.

    Returns:
        Lista de dicts com os campos:
          - titulo (str)
          - link (str)
          - data (str, formato DD/MM/YYYY)
          - fonte (str)
    """
    try:
        scraper = cloudscraper.create_scraper()
        response = scraper.get(URL, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        artigos = soup.find_all("article")

        editais = []
        hoje = datetime.now()
        limite = hoje - timedelta(days=JANELA_DIAS)

        for artigo in artigos:
            # Extrai título e link
            titulo_tag = artigo.find("h2", class_="post-title")
            if not titulo_tag:
                continue

            link_tag = titulo_tag.find("a")
            if not link_tag:
                continue

            titulo = link_tag.get_text(strip=True)
            link = link_tag.get("href")

            # Extrai data de publicação
            time_tag = artigo.find("time")
            if not time_tag:
                continue

            data_str = time_tag.get("datetime")
            try:
                data_publicacao = datetime.fromisoformat(data_str)
            except Exception:
                continue

            # Descarta publicações mais antigas que a janela configurada
            if data_publicacao < limite:
                continue

            editais.append({
                "titulo": titulo,
                "link": link,
                "data": data_publicacao.strftime("%d/%m/%Y"),
                "fonte": FONTE,
            })

        return editais

    except Exception as e:
        print(f"  ⚠ Erro ao coletar Observatório do Terceiro Setor: {e}")
        return []
