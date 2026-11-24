import re
from bs4 import BeautifulSoup

ANO_RE = re.compile(r"(?<![\d.,])(?:19|20)\d{2}(?![\d.,])")
NUM_RE = re.compile(r"\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+(?:,\d+)?")


def _linhas(soup: BeautifulSoup) -> list[str]:
    return [l.strip() for l in soup.get_text("\n").split("\n") if l.strip()]


def _bloco(linhas: list[str], rotulo: str, tamanho: int = 5) -> list[str]:
    for i, linha in enumerate(linhas):
        if linha.lower().startswith(rotulo.lower()):
            return linhas[i : i + tamanho]
    return []


def _ano(texto: str) -> int | None:
    m = ANO_RE.search(texto)
    return int(m.group()) if m else None


def _numero_br(texto: str, decimal: bool) -> int | float | None:
    sem_ano = ANO_RE.sub(" ", texto)
    m = NUM_RE.search(sem_ano)
    if not m:
        return None
    bruto = m.group().replace(".", "").replace(",", ".")
    try:
        return float(bruto) if decimal else int(float(bruto))
    except ValueError:
        return None


def _primeiro_texto(bloco: list[str]) -> str | None:
    """Primeira linha após o rótulo que seja texto de verdade (não ano/colchetes)."""
    for linha in bloco[1:]:
        limpa = re.sub(r"[\[\]()]", "", ANO_RE.sub("", linha)).strip()
        if limpa and re.search(r"[A-Za-zÀ-ÿ]", limpa):
            return limpa
    return None


def extrair(html: str) -> tuple[dict, list[str]]:
    """Retorna (dados, lista_de_campos_ausentes)."""
    soup = BeautifulSoup(html, "html.parser")
    linhas = _linhas(soup)

    b_pref = _bloco(linhas, "Prefeito")
    b_gent = _bloco(linhas, "Gentílico")
    b_pop = _bloco(linhas, "População estimada")
    b_area = _bloco(linhas, "Área territorial")

    texto_pop = " ".join(b_pop)
    texto_area = " ".join(b_area)

    dados = {
        "prefeito": _primeiro_texto(b_pref) if b_pref else None,
        "gentilico": _primeiro_texto(b_gent) if b_gent else None,
        "populacao_estimada": _numero_br(texto_pop, decimal=False) if b_pop else None,
        "ano_populacao": _ano(texto_pop) if b_pop else None,
        "area_km2": _numero_br(texto_area, decimal=True) if b_area else None,
        "ano_area": _ano(texto_area) if b_area else None,
    }
    ausentes = [campo for campo, valor in dados.items() if valor is None]
    return dados, ausentes