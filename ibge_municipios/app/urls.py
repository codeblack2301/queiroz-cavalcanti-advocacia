import re
import unicodedata
from app import config


def slugify(nome: str) -> str:
    sem_acento = "".join(
        c for c in unicodedata.normalize("NFKD", nome) if not unicodedata.combining(c)
    )
    return re.sub(r"[^a-z0-9]+", "-", sem_acento.lower()).strip("-")


def montar_url(uf: str, municipio: str) -> str:
    return f"{config.PORTAL_BASE}/{uf.lower()}/{slugify(municipio)}.html"