"""
Edital Alert Bot — Ponto de entrada principal.

Fluxo:
  1. Coleta editais de todas as fontes registradas em `fontes`
  2. Filtra editais já processados (via storage)
  3. Classifica cada edital com o Google Gemini
  4. Envia e-mail com os editais relevantes
  5. Marca os enviados no storage para não reprocessar
"""

from dotenv import load_dotenv

# Carrega variáveis do arquivo .env (útil para execução local)
load_dotenv()

from src.bot_alertas.collectors.prosas import collect_bs
from src.bot_alertas.collectors.observatorio_terceiro_setor import coletar as coletar_observatorio

from src.bot_alertas.filter import classificar_com_gemini
from src.bot_alertas.storage.storage import (
    ja_processado,
    salvar_resultado,
    marcar_como_enviado,
)
from src.bot_alertas.email_service import send_email

# ============================================================
# Registro de coletores
# Adicione novos coletores aqui para ampliar as fontes monitoradas.
# Cada coletor deve retornar uma lista de dicts com ao menos:
#   { "titulo": str, "link": str, "fonte": str }
# ============================================================
fontes = [
    collect_bs,
    coletar_observatorio,
]


def main():
    print("🔎 Coletando editais...")
    editais = []

    for coletar in fontes:
        try:
            novos = coletar()
            print(f"  ✔ {coletar.__module__}: {len(novos)} edital(is) coletado(s)")
            editais.extend(novos)
        except Exception as e:
            print(f"  ✖ Erro no coletor {coletar.__module__}: {e}")

    if not editais:
        print("⚠ Nenhum edital coletado. Encerrando.")
        return

    print(f"\n📦 Total coletado (todas as fontes): {len(editais)}")

    print("\n🧠 Iniciando classificação com IA...")
    relevantes = []

    for edital in editais:
        link = edital.get("link")
        if not link:
            continue

        # Evita reprocessar editais já classificados anteriormente
        if ja_processado(link):
            continue

        texto_completo = f"""
        Título: {edital.get('titulo', '')}
        Organização: {edital.get('organizacao', '')}
        Fonte: {edital.get('fonte', '')}
        """

        resultado = classificar_com_gemini(texto_completo)

        # Persiste o resultado no storage (relevante ou não)
        salvar_resultado(link, resultado)

        if resultado.get("relevante"):
            relevantes.append(edital)

    print(f"\n🎯 Editais relevantes encontrados: {len(relevantes)}")

    # Envia e-mail (com ou sem editais relevantes)
    send_email(relevantes)

    # Marca como enviado para não reenviar nas próximas execuções
    for edital in relevantes:
        link = edital.get("link")
        if link:
            marcar_como_enviado(link)

    print("\n✅ Processo finalizado com sucesso.")


if __name__ == "__main__":
    main()
