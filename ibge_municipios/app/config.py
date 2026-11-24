from pathlib import Path

HEADLESS = True              
MAX_BLOQUEIOS_SEGUIDOS = 3   

API_BASE = "https://servicodados.ibge.gov.br/api/v1/localidades"
PORTAL_BASE = "https://www.ibge.gov.br/cidades-e-estados"
LIMITE_PADRAO = 5
PAUSA_ENTRE_PAGINAS = 2.0     
TIMEOUT_API = 20               
TIMEOUT_PAGINA_MS = 30_000
OUTPUT_DIR = Path("output")
LOG_DIR = Path("logs")
COLUNAS = [
    "codigo_ibge", "municipio", "uf", "regiao", "prefeito", "gentilico",
    "populacao_estimada", "ano_populacao", "area_km2", "ano_area",
    "url_fonte", "data_coleta",
]