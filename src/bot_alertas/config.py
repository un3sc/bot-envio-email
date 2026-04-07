"""
Configuração das fontes de coleta.

- RSS_SOURCES: feeds RSS que serão consumidos pelo rss_collector
- STATIC_SOURCES: páginas estáticas que serão raspadas pelo scraper_static

Adicione quantas fontes desejar — o bot processará todas automaticamente.
"""

# Feeds RSS de fontes de editais.
# Formato: { "Nome Exibido": "URL do feed RSS" }
RSS_SOURCES = {
    # Exemplo:
    # "Minha Fonte": "https://minhafonte.org.br/feed/rss",
}

# Páginas estáticas para scraping simples (busca links com "edital" no texto).
# Formato: { "Nome Exibido": "URL da página" }
STATIC_SOURCES = {
    # Exemplo:
    # "Prefeitura de SP": "https://www.prefeitura.sp.gov.br/editais",
}
