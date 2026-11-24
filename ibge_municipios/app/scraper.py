from playwright.sync_api import (
    sync_playwright,
    Error as PWError,
    TimeoutError as PWTimeout,
)
from app import config

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)


class PaginaNaoEncontrada(Exception):
    pass


class ErroDeNavegacao(Exception):
    pass


class AcessoBloqueado(Exception):
    pass


class Navegador:
    def __enter__(self):
        self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.launch(headless=config.HEADLESS)
        self._context = self._browser.new_context(
            user_agent=USER_AGENT,
            locale="pt-BR",
            viewport={"width": 1366, "height": 768},
        )
        self._page = self._context.new_page()
        return self

    def __exit__(self, *args):
        # fecha tudo mesmo se algo deu errado
        try:
            self._browser.close()
        finally:
            self._pw.stop()

    def obter_html(self, url: str) -> str:
        try:
            resp = self._page.goto(
                url, wait_until="domcontentloaded", timeout=config.TIMEOUT_PAGINA_MS
            )
        except PWTimeout as e:
            raise ErroDeNavegacao(f"Timeout em {url}") from e
        except PWError as e:
            raise ErroDeNavegacao(f"Falha em {url}: {e}") from e

        if resp is not None:
            if resp.status == 404:
                raise PaginaNaoEncontrada(url)
            if resp.status in (401, 403, 429):
                raise AcessoBloqueado(f"HTTP {resp.status} em {url}")
            if resp.status >= 400:
                raise ErroDeNavegacao(f"HTTP {resp.status} em {url}")

        try:
            # a página carrega os dados via JavaScript; espera o rótulo aparecer
            self._page.wait_for_selector("text=Gentílico", timeout=15_000)
        except PWTimeout as e:
            raise PaginaNaoEncontrada(f"Conteúdo esperado ausente: {url}") from e

        return self._page.content()