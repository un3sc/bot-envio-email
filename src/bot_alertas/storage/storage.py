"""
Módulo de persistência de editais processados.

Usa um arquivo JSON local (storage.json) para registrar quais editais
já foram classificados e/ou enviados por e-mail, evitando reprocessamento
e reenvio nas próximas execuções.

Estrutura do storage.json:
{
    "editais_processados": {
        "https://link-do-edital.com": {
            "relevante": true/false,
            "justificativa": "...",
            "data_classificacao": "2026-01-01T00:00:00",
            "enviado": true/false
        },
        ...
    }
}
"""

import json
from datetime import datetime
from pathlib import Path

# Caminho do arquivo de storage (relativo a este módulo)
BASE_DIR = Path(__file__).resolve().parent
STORAGE_FILE = BASE_DIR / "storage.json"


# ============================================================
# Funções internas
# ============================================================

def _estrutura_padrao() -> dict:
    return {"editais_processados": {}}


def _garantir_arquivo() -> None:
    """Cria o arquivo storage.json caso não exista."""
    if not STORAGE_FILE.exists():
        _escrever_arquivo(_estrutura_padrao())


def _ler_arquivo() -> dict:
    """Lê e retorna o conteúdo do storage. Recria se estiver corrompido."""
    _garantir_arquivo()
    try:
        with open(STORAGE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        dados = _estrutura_padrao()
        _escrever_arquivo(dados)
        return dados


def _escrever_arquivo(dados: dict) -> None:
    """Escreve o storage de forma atômica (arquivo temporário → rename)."""
    temp_path = STORAGE_FILE.with_suffix(".tmp")
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)
    temp_path.replace(STORAGE_FILE)


# ============================================================
# API pública
# ============================================================

def ja_processado(link: str) -> bool:
    """
    Verifica se um edital já foi classificado anteriormente.

    Args:
        link: URL única do edital.

    Returns:
        True se o edital já está no storage.
    """
    dados = _ler_arquivo()
    return link in dados.get("editais_processados", {})


def salvar_resultado(link: str, resultado_llm: dict, enviado: bool = False) -> None:
    """
    Salva o resultado da classificação de um edital no storage.

    Args:
        link: URL única do edital.
        resultado_llm: dict retornado pelo classificador (deve ter "relevante").
        enviado: True se o edital já foi incluído em algum e-mail enviado.
    """
    dados = _ler_arquivo()
    editais = dados.get("editais_processados", {})

    relevante = resultado_llm.get("relevante", False)
    if isinstance(relevante, str):
        relevante = relevante.lower() in ("sim", "true", "1", "yes")

    editais[link] = {
        "relevante": relevante,
        "justificativa": resultado_llm.get("justificativa", ""),
        "data_classificacao": datetime.utcnow().isoformat(),
        "enviado": enviado,
    }

    dados["editais_processados"] = editais
    _escrever_arquivo(dados)


def marcar_como_enviado(link: str) -> None:
    """
    Marca um edital como enviado no storage.

    Args:
        link: URL única do edital.
    """
    dados = _ler_arquivo()
    if link in dados.get("editais_processados", {}):
        dados["editais_processados"][link]["enviado"] = True
        _escrever_arquivo(dados)


def obter_pendentes_envio() -> list[str]:
    """
    Retorna links de editais relevantes que ainda não foram enviados por e-mail.

    Útil para reenviar alertas sem reclassificar.

    Returns:
        Lista de URLs pendentes.
    """
    dados = _ler_arquivo()
    return [
        link
        for link, info in dados.get("editais_processados", {}).items()
        if info.get("relevante") and not info.get("enviado")
    ]
