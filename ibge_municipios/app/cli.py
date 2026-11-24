from app import config


def escolher_estado(estados: list[dict]) -> dict:
    print("\nEstados disponíveis:")
    for i, e in enumerate(estados, start=1):
        print(f"  {i:>2}. {e['sigla']} - {e['nome']}")
    while True:
        entrada = input("\nDigite o número ou a sigla da UF: ").strip().upper()
        if entrada.isdigit() and 1 <= int(entrada) <= len(estados):
            return estados[int(entrada) - 1]
        for e in estados:
            if e["sigla"] == entrada:
                return e
        print("Seleção inválida. Tente de novo.")


def escolher_limite(total: int) -> int:
    padrao = min(config.LIMITE_PADRAO, total)
    while True:
        entrada = input(
            f"Quantos municípios processar? (1 a {total}, Enter = {padrao}): "
        ).strip()
        if not entrada:
            return padrao
        if entrada.isdigit() and int(entrada) >= 1:
            return min(int(entrada), total)   # nunca passa do total da API
        print("Valor inválido. Digite um número inteiro positivo.")