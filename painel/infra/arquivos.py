import csv
import json
from pathlib import Path

from ..core.entidades import Configuracao


def ler_csv(caminho: str | Path) -> list[tuple[int, dict[str, str]]]:
    registros: list[tuple[int, dict[str, str]]] = []
    with open(caminho, "r", encoding="utf-8", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        for linha, registro in enumerate(leitor, start=2):
            registros.append((linha, registro))
    return registros


def ler_configuracao(caminho: str | Path) -> Configuracao:
    with open(caminho, "r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)
    return Configuracao(
        media_aprovacao=float(dados["media_aprovacao"]),
        media_recuperacao=float(dados["media_recuperacao"]),
        nota_maxima=float(dados["nota_maxima"]),
    )
