"""
Coletor genérico de feeds RSS.

Processa todos os feeds definidos em `config.RSS_SOURCES` e retorna
entradas publicadas nos últimos 30 dias.

Para adicionar novas fontes RSS, edite `src/bot_alertas/config.py`:

    RSS_SOURCES = {
        "Nome da Fonte": "https://url-do-feed.com/rss",
    }
"""

import feedparser
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime

from ..config import RSS_SOURCES

# Janela de busca: considera publicações dos últimos N dias
JANELA_DIAS = 30


def coletar_rss() -> list[dict]:
    """
    Coleta entradas recentes de todos os feeds RSS configurados.

    Returns:
        Lista de dicts com os campos:
          - fonte (str)
          - titulo (str)
          - resumo (str)
          - link (str)
          - data (str, formato DD/MM/YYYY)
    """
    resultados = []
    hoje = datetime.now()
    limite = hoje - timedelta(days=JANELA_DIAS)

    for fonte, url in RSS_SOURCES.items():
        try:
            feed = feedparser.parse(url)

            if not feed.entries:
                print(f"  ⚠ Nenhuma entrada no feed: {fonte}")
                continue

            for entry in feed.entries:
                data_publicacao = None

                # Tenta extrair a data de publicação (published ou updated)
                for campo in ("published", "updated"):
                    if hasattr(entry, campo):
                        try:
                            data_publicacao = parsedate_to_datetime(getattr(entry, campo))
                            break
                        except Exception:
                            pass

                if not data_publicacao:
                    continue

                # Remove timezone para comparação com datetime naive
                data_naive = data_publicacao.replace(tzinfo=None)
                if data_naive < limite:
                    continue

                resultados.append({
                    "fonte": fonte,
                    "titulo": entry.title,
                    "resumo": getattr(entry, "summary", ""),
                    "link": entry.link,
                    "data": data_naive.strftime("%d/%m/%Y"),
                })

        except Exception as e:
            print(f"  ⚠ Erro ao processar feed RSS '{fonte}': {e}")

    return resultados
