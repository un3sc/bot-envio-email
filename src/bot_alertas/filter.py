"""
Módulo de classificação de editais.

Usa dois filtros em sequência:
  1. Regex (pré-filtro barato): descarta editais claramente fora do escopo
     antes de consumir tokens da API do Gemini.
  2. Google Gemini (classificação semântica): analisa o contexto completo
     e decide se o edital é relevante com base no prompt configurado.

Para adaptar o bot ao seu contexto, edite:
  - PADROES_ESTRUTURA: termos que indicam que o texto é um edital/chamada
  - PADROES_TEMA: termos do seu nicho de atuação
  - montar_prompt(): critérios de relevância detalhados para a IA
"""

import os
import re
import unicodedata

from google import genai
from google.genai import types

# ============================================================
# Configuração do cliente Gemini
# ============================================================

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# gemini-1.5-flash tem camada gratuita generosa e boa capacidade de classificação
MODEL_NAME = "gemini-1.5-flash"


# ============================================================
# Schema de resposta estruturada
# ============================================================

schema = types.Schema(
    type=types.Type.OBJECT,
    properties={
        "relevante": types.Schema(type=types.Type.BOOLEAN),
        "titulo": types.Schema(type=types.Type.STRING),
        "organizacao": types.Schema(type=types.Type.STRING),
        "data_publicacao": types.Schema(type=types.Type.STRING),
        "data_encerramento": types.Schema(type=types.Type.STRING),
        "resumo_curto": types.Schema(type=types.Type.STRING),
    },
    required=["relevante"],
)


# ============================================================
# Pré-filtro por regex (filtro 1 — barato)
# ============================================================

# Termos que indicam que o texto descreve um edital/chamada pública
PADROES_ESTRUTURA = [
    r"edital",
    r"chamada p[uú]blica",
    r"sele[cç][aã]o p[uú]blica",
    r"pol[ií]tica de fomento",
    r"apoio financeiro",
    r"subven[cç][aã]o",
]

# Termos do nicho de atuação — edite conforme seu contexto
PADROES_TEMA = [
    r"cursinho popular",
    r"pré[- ]?vestibular",
    r"educa[cç][aã]o popular",
    r"educa[cç][aã]o comunit[aá]ria",
]


def normalizar(texto: str) -> str:
    """Remove acentos e converte para minúsculas para comparação robusta."""
    texto = texto.lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")
    return texto


def passa_pre_filtro(texto: str) -> bool:
    """
    Retorna True se o texto contém ao menos um termo estrutural
    E ao menos um termo temático — ou seja, parece ser um edital
    dentro do escopo de interesse.
    """
    texto = normalizar(texto)
    tem_estrutura = any(re.search(p, texto) for p in PADROES_ESTRUTURA)
    tem_tema = any(re.search(p, texto) for p in PADROES_TEMA)
    return tem_estrutura and tem_tema


# ============================================================
# Prompt para o Gemini (filtro 2 — semântico)
# ============================================================

def montar_prompt(texto: str) -> str:
    """
    Monta o prompt enviado ao Gemini para classificação semântica.

    ✏️  PERSONALIZE AQUI:
    Ajuste os critérios de relevância (seções "Marque relevante=true" e
    "Marque relevante=false") para o contexto da sua organização.
    """
    return f"""
Você é um classificador especializado em editais públicos.

Objetivo: identificar se o edital é relevante para as seguintes áreas:

- Cursinhos populares
- Pré-vestibulares comunitários
- Educação popular
- Projetos de acesso ao ensino superior
- Políticas públicas de fomento relacionadas a essas áreas

Critérios de decisão:

1. Marque relevante=true se o edital mencionar explicitamente OU estiver claramente
   direcionado a:
   - Cursinhos comunitários ou populares
   - Pré-vestibulares sociais
   - Ações de democratização do acesso ao ensino superior
   - Iniciativas de educação popular
   - Políticas de apoio financeiro, estrutural ou institucional para essas iniciativas
   - O local de atuação deve ser São Paulo ou de abrangência nacional

2. Marque relevante=false se:
   - O edital for genérico (ex: educação básica ampla, cultura geral, esporte, saúde)
   - Tratar apenas de ensino superior regular sem foco em acesso democrático
   - Não houver evidência clara de relação com os temas listados
   - O local de atuação não for São Paulo nem nacional

Regras importantes:
- Não faça suposições além do texto fornecido.
- Baseie-se apenas nas informações presentes.
- Em caso de dúvida razoável, marque relevante=false.

Retorne APENAS um objeto JSON válido, sem texto adicional, seguindo esta estrutura:

{{
  "relevante": true ou false,
  "justificativa": "explicação curta baseada no texto"
}}

Texto do edital:
\"\"\"
{texto}
\"\"\"
"""


# ============================================================
# Classificação principal com Gemini
# ============================================================

def classificar_com_gemini(texto: str) -> dict:
    """
    Envia o texto do edital ao Gemini e retorna o resultado da classificação.

    Retorna:
        dict com ao menos a chave "relevante" (bool).
        Pode conter também: titulo, organizacao, data_encerramento, resumo_curto.
        Em caso de erro, retorna {"relevante": False}.
    """
    try:
        # Limita o texto para economizar tokens (ajuste se necessário)
        texto = texto[:4000]

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=montar_prompt(texto),
            config=types.GenerateContentConfig(
                temperature=0,
                response_mime_type="application/json",
                response_schema=schema,
            ),
        )

        if response.parsed:
            parsed = response.parsed

            # Normaliza o campo "relevante" caso venha como string
            if isinstance(parsed.get("relevante"), str):
                parsed["relevante"] = parsed["relevante"].strip().lower() in (
                    "true", "1", "sim", "yes"
                )

            return parsed

        return {"relevante": False}

    except Exception as e:
        print(f"  ⚠ Erro na classificação Gemini: {e}")
        return {"relevante": False}


# ============================================================
# Função auxiliar: filtragem em lote (com pré-filtro regex)
# ============================================================

def filtrar_editais(editais: list) -> list:
    """
    Filtra uma lista de editais aplicando pré-filtro regex + Gemini.

    Use esta função se quiser aplicar o pré-filtro antes de chamar o Gemini,
    economizando tokens em lotes grandes. O main.py atual chama o Gemini
    diretamente sem o pré-filtro regex — ambas as abordagens funcionam.

    Args:
        editais: lista de dicts com ao menos "titulo", "fonte", "link"

    Returns:
        lista dos editais classificados como relevantes pelo Gemini,
        com os campos do resultado mesclados.
    """
    relevantes = []

    for edital in editais:
        areas = ", ".join(edital.get("areas", [])) if edital.get("areas") else ""

        texto_completo = f"""
        Título: {edital.get('titulo', '')}
        Organização: {edital.get('organizacao', '')}
        Áreas: {areas}
        Fonte: {edital.get('fonte', '')}
        """

        # Pré-filtro regex — evita chamar o Gemini em editais claramente fora do escopo
        if not passa_pre_filtro(texto_completo):
            continue

        resultado_llm = classificar_com_gemini(texto_completo)

        if resultado_llm and resultado_llm.get("relevante"):
            edital.update(resultado_llm)
            relevantes.append(edital)

    return relevantes
