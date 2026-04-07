# 📢 Edital Alert Bot

Um bot automatizado para monitorar e filtrar editais públicos relevantes para **cursinhos populares, pré-vestibulares comunitários e projetos de educação popular**, enviando alertas por e-mail com os resultados.

Adaptável para qualquer organização do terceiro setor — basta ajustar os critérios de relevância no prompt da IA.

---

## ✨ Funcionalidades

- 🔍 Coleta automatizada de editais de múltiplas fontes (Prosas, Observatório do Terceiro Setor e mais)
- 🤖 Classificação inteligente com IA (Google Gemini) para filtrar apenas editais relevantes
- 📧 Envio de e-mail em HTML com os editais encontrados
- 💾 Armazenamento local para evitar reprocessamento de editais já analisados
- ⚙️ Execução automática via GitHub Actions (configurável — padrão: terças e quintas)

---

## 🗂️ Estrutura do Projeto

```
edital-alert-bot/
├── main.py                                     # Ponto de entrada principal
├── requirements.txt                            # Dependências Python
├── .env.example                                # Modelo de variáveis de ambiente
├── .github/
│   └── workflows/
│       └── alert.yml                           # Workflow do GitHub Actions
└── src/
    └── bot_alertas/
        ├── config.py                           # Fontes RSS e estáticas configuráveis
        ├── filter.py                           # Filtro com Gemini (IA) + regex
        ├── email_service.py                    # Geração e envio de e-mail HTML
        ├── collectors/
        │   ├── prosas.py                       # Coletor da API do Prosas
        │   ├── observatorio_terceiro_setor.py  # Coletor via scraping
        │   ├── rss_collector.py                # Coletor genérico de feeds RSS
        │   ├── scraper_static.py               # Coletor genérico de páginas estáticas
        │   └── dou_collector.py                # Coletor do Diário Oficial da União
        └── storage/
            ├── storage.py                      # Lógica de persistência (JSON)
            └── storage.json                    # Banco de dados local (gerado automaticamente)
```

---

## 🚀 Como Usar

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/edital-alert-bot.git
cd edital-alert-bot
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Configure as variáveis de ambiente

Copie o arquivo de exemplo e preencha com seus dados:

```bash
cp .env.example .env
```

Edite o `.env`:

```env
EMAIL_USER=seu_email@gmail.com
EMAIL_PASSWORD=sua_senha_de_app_gmail
EMAIL_TO=destinatario@email.com
GEMINI_API_KEY=sua_chave_api_gemini
```

> **Atenção:** Para o Gmail, você precisa gerar uma [Senha de App](https://support.google.com/accounts/answer/185833) — não use sua senha comum.

### 4. Execute localmente

```bash
python main.py
```

---

## ⚙️ Configuração

### Personalizar os critérios de relevância

O coração do bot é o prompt da IA em `src/bot_alertas/filter.py`. Edite a função `montar_prompt()` para ajustar quais editais são considerados relevantes para sua organização:

```python
# Em filter.py → montar_prompt()
"""
Objetivo: identificar se o edital é relevante para:
- Cursinhos populares
- Pré-vestibulares comunitários
- ...adicione seus critérios aqui
"""
```

Também ajuste os padrões de regex para o pré-filtro barato:

```python
# Em filter.py
PADROES_TEMA = [
    r"cursinho popular",
    r"pré[- ]?vestibular",
    r"minha área de atuação",   # ← adicione aqui
]
```

### Adicionar novas fontes RSS

Edite `src/bot_alertas/config.py`:

```python
RSS_SOURCES = {
    "Nome da Fonte": "https://url-do-feed-rss.com/feed",
}
```

### Adicionar novas fontes estáticas (scraping simples)

```python
STATIC_SOURCES = {
    "Nome da Fonte": "https://url-da-pagina.com.br/editais",
}
```

### Criar um coletor customizado

Crie um arquivo em `src/bot_alertas/collectors/meu_coletor.py`:

```python
def meu_coletor():
    editais = []
    # Sua lógica de coleta aqui
    editais.append({
        "titulo": "Título do edital",
        "link": "https://link-do-edital.com",
        "fonte": "Nome da Fonte",
        "data": "01/01/2025",
    })
    return editais
```

Registre-o em `main.py`:

```python
from src.bot_alertas.collectors.meu_coletor import meu_coletor

fontes = [
    collect_bs,
    coletar_observatorio,
    meu_coletor,  # ← adicione aqui
]
```

---

## 🤖 Automação com GitHub Actions

O bot é executado automaticamente duas vezes por semana via GitHub Actions.

### Configurar os Secrets no GitHub

Vá em **Settings → Secrets and variables → Actions** e adicione:

| Secret | Descrição |
|---|---|
| `EMAIL_USER` | E-mail de envio (Gmail) |
| `EMAIL_PASSWORD` | Senha de App do Gmail |
| `EMAIL_TO` | E-mail(s) de destino |
| `GEMINI_API_KEY` | Chave da API do Google Gemini |

### Executar manualmente

Na aba **Actions** do GitHub, selecione **Edital Alert Bot** e clique em **Run workflow**.

### Personalizar o agendamento

Edite `.github/workflows/alert.yml`:

```yaml
on:
  schedule:
    # Formato cron (UTC): minuto hora dia mês dia-semana
    - cron: '0 21 * * 2,4'   # Terças e quintas às 21h UTC (18h BRT)
```

---

## 🧠 Como Funciona a Classificação

O sistema usa dois filtros em sequência para equilibrar custo e precisão:

```
Edital coletado
      │
      ▼
┌─────────────────────────┐
│  Filtro 1: Regex        │  ← Rápido e gratuito
│  (palavras-chave)       │
└─────────────────────────┘
      │ Passou?
      ▼
┌─────────────────────────┐
│  Filtro 2: Gemini (IA)  │  ← Análise semântica
│  (classificação LLM)    │
└─────────────────────────┘
      │ Relevante?
      ▼
   Enviado por e-mail + salvo no storage
```

**Filtro 1 (Regex):** Verifica se o texto contém termos estruturais (ex: "edital", "chamada pública") E termos temáticos (ex: "cursinho popular", "pré-vestibular"). Editais que não passam aqui não chegam ao Gemini — economia de tokens.

**Filtro 2 (Gemini):** Analisa o contexto completo com o prompt configurado e decide se o edital é de fato relevante para o público-alvo.

> **Nota:** O `main.py` atual envia todos os editais coletados para o Gemini diretamente (sem o pré-filtro regex). Para ativar o pré-filtro, use a função `filtrar_editais()` de `filter.py` no lugar da classificação individual.

---

## 🔑 Obtendo a Chave da API Gemini

1. Acesse [Google AI Studio](https://aistudio.google.com/)
2. Clique em **Get API Key**
3. Crie ou selecione um projeto Google Cloud
4. Copie a chave gerada

O modelo usado é `gemini-1.5-flash`, que possui uma [camada gratuita generosa](https://ai.google.dev/pricing).

---

## 🤝 Como Contribuir

Contribuições são muito bem-vindas!

1. Faça um **fork** do projeto
2. Crie uma branch: `git checkout -b feature/nova-fonte`
3. Commit suas mudanças: `git commit -m 'feat: adiciona coletor do BNDES'`
4. Push para a branch: `git push origin feature/nova-fonte`
5. Abra um **Pull Request**

### Ideias de contribuição

- Novos coletores de fontes de editais (BNDES, fundações estaduais, etc.)
- Suporte a notificações via Telegram ou WhatsApp
- Interface web para visualizar editais coletados
- Testes automatizados
- Suporte a múltiplos perfis de relevância simultâneos

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 💜 Sobre

Este projeto nasceu da necessidade de cursinhos populares e organizações do terceiro setor acompanharem editais de fomento de forma eficiente e automatizada.

Se ele te ajudou, considere dar uma ⭐ e compartilhar com outras organizações!
