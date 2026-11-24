import unicodedata
import httpx
from app import config


class ApiError(Exception):
    """Falha ao consultar a API de Localidades."""


def _chave_ordenacao(texto: str) -> str:
    sem_acento = "".join(
        c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c)
    )
    return sem_acento.casefold()


def _get_json(url: str):
    try:
        resp = httpx.get(url, timeout=config.TIMEOUT_API, follow_redirects=True)
        resp.raise_for_status()
        return resp.json()
    except httpx.TimeoutException as e:
        raise ApiError(f"Tempo esgotado ao acessar {url}") from e
    except httpx.HTTPStatusError as e:
        raise ApiError(f"HTTP {e.response.status_code} em {url}") from e
    except httpx.HTTPError as e:
        raise ApiError(f"Erro de rede em {url}: {e}") from e
    except ValueError as e:
        raise ApiError(f"Resposta JSON inválida em {url}") from e


def listar_estados() -> list[dict]:
    dados = _get_json(f"{config.API_BASE}/estados")
    try:
        estados = [
            {"sigla": e["sigla"], "nome": e["nome"], "regiao": e["regiao"]["nome"]}
            for e in dados
        ]
    except (KeyError, TypeError) as e:
        raise ApiError("Formato inesperado na lista de estados") from e
    return sorted(estados, key=lambda e: _chave_ordenacao(e["nome"]))


def listar_municipios(uf: str) -> list[dict]:
    dados = _get_json(f"{config.API_BASE}/estados/{uf}/municipios")
    try:
        municipios = [
            {"codigo_ibge": str(m["id"]).zfill(7), "nome": m["nome"]} for m in dados
        ]
    except (KeyError, TypeError) as e:
        raise ApiError("Formato inesperado na lista de municípios") from e
    return sorted(municipios, key=lambda m: _chave_ordenacao(m["nome"]))