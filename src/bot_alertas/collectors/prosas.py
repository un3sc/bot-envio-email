"""
Coletor de editais da plataforma Prosas (prosas.com.br).

Consome a API pública de oportunidades e retorna editais com prazo
de inscrição aberto nos próximos 60 dias.

API: https://prosas.com.br/selecao/api/v2/publics/oportunidades
"""

import requests
from datetime import datetime, timedelta, timezone

BASE_URL = "https://prosas.com.br/selecao/api/v2/publics/oportunidades"

HEADERS = {
    "Content-Type": "application/vnd.api+json",
    "Locale": "pt",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
}

# Janela de busca: coleta editais com encerramento nos próximos N dias
JANELA_DIAS = 60
PAGE_SIZE = 50


def collect_bs() -> list[dict]:
    """
    Coleta oportunidades abertas na plataforma Prosas.

    Returns:
        Lista de dicts com os campos:
          - fonte (str)
          - titulo (str)
          - link (str)
          - data_encerramento (str, formato DD/MM/YYYY HH:MM)
    """
    resultados = []
    hoje = datetime.now(timezone.utc)
    limite_superior = hoje + timedelta(days=JANELA_DIAS)
    pagina = 1

    while True:
        try:
            params = {
                "page[page]": pagina,
                "page[size]": PAGE_SIZE,
                "include": "area_interesses,incentivador",
            }

            response = requests.get(
                BASE_URL,
                headers=HEADERS,
                params=params,
                timeout=20,
            )
            response.raise_for_status()
            data = response.json()

            oportunidades = data.get("data", [])
            if not oportunidades:
                break  # Sem mais páginas

            for item in oportunidades:
                atributos = item.get("attributes", {})
                titulo = atributos.get("nome", "")
                data_encerramento_str = atributos.get("data_final_inscricoes")

                if not data_encerramento_str:
                    continue

                try:
                    data_encerramento = datetime.fromisoformat(data_encerramento_str)
                    if data_encerramento.tzinfo is None:
                        data_encerramento = data_encerramento.replace(tzinfo=timezone.utc)
                except Exception:
                    continue

                # Inclui apenas editais com encerramento na janela configurada
                if hoje <= data_encerramento <= limite_superior:
                    resultados.append({
                        "fonte": "Prosas",
                        "titulo": titulo,
                        "link": f"https://prosas.com.br/editais/{item.get('id')}",
                        "data_encerramento": data_encerramento.strftime("%d/%m/%Y %H:%M"),
                    })

            pagina += 1

        except Exception as e:
            print(f"  ⚠ Erro ao coletar Prosas (página {pagina}): {e}")
            break

    return resultados
