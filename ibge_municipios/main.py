import logging
import time

from app import api, cli, config, export, parser, urls
from app.scraper import (
    Navegador,
    PaginaNaoEncontrada,
    ErroDeNavegacao,
    AcessoBloqueado,
)


def configurar_log():
    config.LOG_DIR.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(config.LOG_DIR / "coleta.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def main():
    configurar_log()
    log = logging.getLogger("main")

    try:
        estados = api.listar_estados()
        estado = cli.escolher_estado(estados)
        uf = estado["sigla"]
        municipios = api.listar_municipios(uf)
    except api.ApiError as e:
        log.error("Não foi possível obter dados da API: %s", e)
        return

    limite = cli.escolher_limite(len(municipios))
    selecionados = municipios[:limite]
    log.info("UF escolhida: %s | processando %d de %d municípios",
             uf, limite, len(municipios))

    registros, nao_encontradas, falhas = [], [], []
    bloqueios_seguidos = 0

    with Navegador() as nav:
        for i, m in enumerate(selecionados):
            if i > 0:
                time.sleep(config.PAUSA_ENTRE_PAGINAS)  # pausa sempre, com ou sem erro

            url = urls.montar_url(uf, m["nome"])
            try:
                html = nav.obter_html(url)
                bloqueios_seguidos = 0
            except PaginaNaoEncontrada:
                log.warning("URL não encontrada: %s", url)
                nao_encontradas.append(url)
                continue
            except AcessoBloqueado as e:
                log.error("Acesso bloqueado: %s", e)
                falhas.append(url)
                bloqueios_seguidos += 1
                if bloqueios_seguidos >= config.MAX_BLOQUEIOS_SEGUIDOS:
                    log.error("Portal bloqueando o acesso. Coleta interrompida.")
                    break
                continue
            except ErroDeNavegacao as e:
                log.error("Falha de navegação: %s", e)
                falhas.append(url)
                continue
            except Exception as e:  # uma página nunca derruba a coleta toda
                log.exception("Erro inesperado em %s: %s", url, e)
                falhas.append(url)
                continue

            dados, ausentes = parser.extrair(html)
            for campo in ausentes:
                log.warning("Campo ausente '%s' em %s", campo, m["nome"])

            registros.append({
                "codigo_ibge": m["codigo_ibge"],
                "municipio": m["nome"],
                "uf": uf,
                "regiao": estado["regiao"],
                **dados,
                "url_fonte": url,
                "data_coleta": export.agora_iso(),
            })
            log.info("OK: %s", m["nome"])

    if not registros:
        log.error("Nenhum município coletado. Planilha não gerada.")
        return

    caminho, total = export.salvar(registros, uf)
    log.info("UF: %s | municípios na planilha: %d | URLs não encontradas: %d | falhas: %d",
             uf, total, len(nao_encontradas), len(falhas))
    log.info("Arquivo gerado: %s", caminho)


if __name__ == "__main__":
    main()