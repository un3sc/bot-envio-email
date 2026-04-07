# Como Contribuir

Obrigado pelo interesse em contribuir com o Edital Alert Bot! 🎉

## Antes de começar

- Verifique se já existe uma [issue](../../issues) aberta sobre o que você quer fazer
- Para mudanças grandes, abra uma issue primeiro para discutir a proposta
- Para correções pequenas (typos, bugs claros), pode abrir o PR diretamente

## Configurando o ambiente de desenvolvimento

```bash
# 1. Fork o repositório e clone
git clone https://github.com/seu-usuario/edital-alert-bot.git
cd edital-alert-bot

# 2. Crie e ative um ambiente virtual
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com suas credenciais
```

## Fluxo de contribuição

```bash
# Crie uma branch descritiva
git checkout -b feat/coletor-bndes
git checkout -b fix/erro-timeout-prosas
git checkout -b docs/adiciona-exemplos-config

# Faça suas alterações e commit
git add .
git commit -m "feat: adiciona coletor de editais do BNDES"

# Envie e abra o PR
git push origin feat/coletor-bndes
```

## Padrão de commits

Usamos [Conventional Commits](https://www.conventionalcommits.org/):

| Prefixo | Uso |
|---|---|
| `feat:` | Nova funcionalidade |
| `fix:` | Correção de bug |
| `docs:` | Documentação |
| `refactor:` | Refatoração sem mudança de comportamento |
| `chore:` | Tarefas de manutenção (deps, CI, etc.) |

## Como criar um novo coletor

1. Crie `src/bot_alertas/collectors/nome_da_fonte.py`
2. Implemente uma função que retorne `list[dict]` com ao menos:
   ```python
   {
       "titulo": str,
       "link": str,       # URL única — usada como chave no storage
       "fonte": str,
       "data": str,       # DD/MM/YYYY
   }
   ```
3. Registre a função em `main.py` na lista `fontes`
4. Documente a fonte no README

## Dúvidas?

Abra uma [issue](../../issues) com a tag `question`.
