# queiroz-cavalcanti-advocacia

# Coletor de municípios do IBGE

Aplicação em Python que lista os estados brasileiros pela API de Localidades do IBGE, permite escolher uma UF, consulta os municípios dela, coleta dados de cada município na página "Cidades e Estados" do portal do IBGE e exporta uma planilha Excel em `output/municipios_{uf}.xlsx`.

## Requisitos

- Python 3.11 ou superior
- Acesso à internet

## Instalação

```bash
# 1. entrar na pasta do projeto
cd ibge_municipios

# 2. criar o ambiente virtual
python -m venv .venv

# 3. ativar o ambiente virtual
#    Windows (PowerShell):
.venv\Scripts\Activate.ps1
#    Windows (Git Bash):
source .venv/Scripts/activate
#    Linux / macOS:
source .venv/bin/activate

# 4. instalar as dependências
python -m pip install -r requirements.txt

# 5. baixar o navegador usado pelo Playwright
python -m playwright install chromium
```

## Como executar

Sempre a partir da pasta `ibge_municipios`, com o ambiente virtual ativo:

```bash
python main.py
```

O programa mostra um menu no terminal:

1. **Escolher o estado:** digite o número da lista (ex.: `17`) ou a sigla (ex.: `PE`).
2. **Escolher o limite:** digite quantos municípios processar ou aperte Enter para usar o padrão (5). O valor nunca ultrapassa o total de municípios retornado pela API.

Os municípios são processados em ordem alfabética.

## Resultado

- Planilha: `output/municipios_{uf}.xlsx` (UF em minúsculas).
- Log da coleta: `logs/coleta.log`.

Colunas, nesta ordem: `codigo_ibge`, `municipio`, `uf`, `regiao`, `prefeito`, `gentilico`, `populacao_estimada`, `ano_populacao`, `area_km2`, `ano_area`, `url_fonte`, `data_coleta`.

## Como ajustar

- **Limite padrão:** `LIMITE_PADRAO` em `app/config.py`.
- **Pausa entre páginas:** `PAUSA_ENTRE_PAGINAS` em `app/config.py` (padrão 2 s).
- **Modo do navegador:** `HEADLESS` em `app/config.py` (`False` abre a janela).

## Fontes

- API de Localidades: `https://servicodados.ibge.gov.br/api/v1/localidades/estados` e `.../estados/{UF}/municipios`
- Portal Cidades e Estados: `https://www.ibge.gov.br/cidades-e-estados/{uf}/{municipio}.html`

## Decisões tomadas

- Nenhum código de estado ou município é fixo: tudo vem da API.
- Playwright é usado porque a página carrega os dados por JavaScript.
- O parser localiza rótulos de texto (Prefeito, Gentílico, População estimada, Área territorial) em vez de classes CSS, que mudam com mais frequência.
- Campos não encontrados ficam vazios na planilha e são registrados no log. Nenhum valor é inventado.
- A falha em uma página não interrompe a coleta. Após 3 bloqueios seguidos (HTTP 401, 403 ou 429), a coleta é interrompida.
- Pausa de 2 s entre páginas e limite padrão baixo, para não sobrecarregar o portal.

## Limitações conhecidas

- Se o layout do portal mudar, o parser precisa de ajuste.
- Nomes com apóstrofo ou caracteres especiais podem gerar uma URL diferente da do portal. Nesses casos a URL é registrada como não encontrada.
- O portal pode bloquear acessos automatizados (HTTP 403). Nesse caso o programa registra o problema e encerra sem gerar planilha.
- Só são processados os primeiros N municípios por ordem de nome.
