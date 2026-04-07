"""
Módulo de envio de e-mail.

Gera e envia e-mails HTML com os editais relevantes encontrados.
Usa SMTP com SSL via Gmail por padrão.

Para usar outro provedor SMTP, ajuste as constantes SMTP_HOST e SMTP_PORT
e as credenciais nas variáveis de ambiente.
"""

import os
import smtplib
from email.mime.text import MIMEText

# ============================================================
# Configuração do servidor SMTP
# ============================================================

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465  # SSL

email_user = os.getenv("EMAIL_USER")
email_password = os.getenv("EMAIL_PASSWORD")
email_to = os.getenv("EMAIL_TO")

if not email_user or not email_password:
    raise ValueError(
        "Credenciais de e-mail não configuradas. "
        "Defina EMAIL_USER e EMAIL_PASSWORD nas variáveis de ambiente."
    )


# ============================================================
# Geração do HTML do e-mail
# ============================================================

# Cor principal do cabeçalho — altere para a identidade visual da sua organização
COR_PRIMARIA = "#4E164A"
COR_PRIMARIA_TEXTO = "#e9d5ff"


def _card_edital(edital: dict) -> str:
    """Gera o bloco HTML de um único card de edital."""
    titulo = edital.get("titulo", "Sem título")
    fonte = edital.get("fonte", "Fonte desconhecida")
    organizacao = edital.get("organizacao", "")
    data = edital.get("data_encerramento", "Não informado")
    link = edital.get("link", "#")
    resumo = edital.get("resumo_curto", "")

    return f"""
    <tr>
        <td style="padding:20px;background:#ffffff;border-radius:12px;
                   border:1px solid #e5e7eb;margin-bottom:20px;">

            <h3 style="margin:0 0 10px 0;color:#292929;font-size:18px;">
                {titulo}
            </h3>

            <p style="margin:0 0 10px 0;color:#6b7280;font-size:13px;line-height:1.5;">
                <strong>Fonte:</strong> {fonte}<br>
                <strong>Organização:</strong> {organizacao}<br>
                <strong>Encerramento:</strong> {data}
            </p>

            <p style="color:#374151;font-size:14px;line-height:1.6;margin:0 0 15px 0;">
                {resumo}
            </p>

            <a href="{link}"
               style="display:inline-block;padding:10px 18px;
                      background-color:{COR_PRIMARIA};
                      color:#ffffff;text-decoration:none;
                      border-radius:8px;font-size:14px;font-weight:bold;">
               Acessar edital
            </a>

        </td>
    </tr>
    <tr><td style="height:20px;"></td></tr>
    """


def _layout_base(titulo_header: str, subtitulo_header: str, conteudo: str) -> str:
    """Envolve o conteúdo no layout HTML base do e-mail."""
    return f"""
    <html>
    <body style="margin:0;padding:0;background:#f3f4f6;font-family:Arial,sans-serif;">
        <table width="100%" cellpadding="0" cellspacing="0" style="padding:30px 0;">
            <tr>
                <td align="center">
                    <table width="700" cellpadding="0" cellspacing="0"
                           style="background:#ffffff;padding:30px;border-radius:16px;">

                        <!-- Cabeçalho -->
                        <tr>
                            <td style="background:{COR_PRIMARIA};
                                       padding:20px 30px;
                                       border-radius:12px 12px 0 0;
                                       text-align:left;">
                                <h2 style="color:#ffffff;margin:0;font-size:20px;">
                                    {titulo_header}
                                </h2>
                                <p style="color:{COR_PRIMARIA_TEXTO};margin:5px 0 0 0;font-size:14px;">
                                    {subtitulo_header}
                                </p>
                            </td>
                        </tr>

                        <tr><td style="height:25px;"></td></tr>

                        <!-- Conteúdo dinâmico -->
                        {conteudo}

                        <!-- Rodapé -->
                        <tr>
                            <td style="padding-top:20px;border-top:1px solid #e5e7eb;
                                       font-size:12px;color:#9ca3af;text-align:center;">
                                Este alerta foi gerado automaticamente pelo
                                <a href="https://github.com/seu-usuario/edital-alert-bot"
                                   style="color:#9ca3af;">Edital Alert Bot</a>.
                            </td>
                        </tr>

                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """


def gerar_html(editais: list) -> str:
    """Gera o HTML completo para e-mail com editais relevantes."""
    cards = "".join(_card_edital(e) for e in editais)
    return _layout_base(
        titulo_header="🚨 Alerta de Editais",
        subtitulo_header="Monitoramento de oportunidades para cursinhos populares",
        conteudo=cards,
    )


def gerar_html_sem_editais() -> str:
    """Gera o HTML para e-mail quando nenhum edital relevante foi encontrado."""
    conteudo = """
    <tr>
        <td style="text-align:left;">
            <p style="color:#374151;font-size:16px;margin:0 0 15px 0;">
                Hoje não foram encontrados novos editais relevantes.
            </p>
            <p style="color:#6b7280;font-size:14px;margin:0;">
                Continue acompanhando — o bot monitorará automaticamente nas próximas execuções.
            </p>
        </td>
    </tr>
    """
    return _layout_base(
        titulo_header="✅ Alerta de Editais",
        subtitulo_header="Monitoramento de oportunidades para cursinhos populares",
        conteudo=conteudo,
    )


# ============================================================
# Envio do e-mail
# ============================================================

def send_email(editais: list) -> None:
    """
    Envia o e-mail de alerta com os editais relevantes.

    Args:
        editais: lista de dicts dos editais relevantes. Pode ser vazia —
                 nesse caso envia um e-mail informando que não há novidades.
    """
    if not editais:
        corpo = gerar_html_sem_editais()
        assunto = "😕 Nenhum edital relevante encontrado"
    else:
        corpo = gerar_html(editais)
        assunto = f"🚨 {len(editais)} novo(s) edital(is) encontrado(s)"

    msg = MIMEText(corpo, "html")
    msg["Subject"] = assunto
    msg["From"] = email_user
    msg["To"] = email_to

    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            server.login(email_user, email_password)
            server.send_message(msg)
        print(f"📧 E-mail enviado com sucesso para {email_to}")
    except Exception as e:
        print(f"✖ Falha ao enviar e-mail: {e}")
        raise
