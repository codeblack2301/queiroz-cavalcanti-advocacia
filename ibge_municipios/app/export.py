from datetime import datetime
import pandas as pd
from app import config


def salvar(registros: list[dict], uf: str):
    config.OUTPUT_DIR.mkdir(exist_ok=True)
    df = pd.DataFrame(registros, columns=config.COLUNAS)

    df = df.drop_duplicates(subset="codigo_ibge")
    df["codigo_ibge"] = df["codigo_ibge"].astype(str).str.zfill(7)
    for col in ["populacao_estimada", "ano_populacao", "ano_area"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
    df["area_km2"] = pd.to_numeric(df["area_km2"], errors="coerce")

    # ordena por nome sem considerar acentos/maiúsculas
    df = df.sort_values(
        "municipio", key=lambda s: s.str.normalize("NFKD").str.casefold()
    ).reset_index(drop=True)

    caminho = config.OUTPUT_DIR / f"municipios_{uf.lower()}.xlsx"
    df.to_excel(caminho, index=False, engine="openpyxl")
    return caminho, len(df)


def agora_iso() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")