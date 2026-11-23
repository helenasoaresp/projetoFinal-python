import argparse
import logging
from pathlib import Path

from .infra.relatorios import RelatorioJSON, RelatorioTexto
from .services.processamento import processar

logger = logging.getLogger(__name__)

def configurar_argumentos() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Painel de notas da turma")
    parser.add_argument("--alunos", default="data/alunos.csv")
    parser.add_argument("--notas", default="data/notas.csv")
    parser.add_argument("--config", default="data/config.json")
    parser.add_argument("--formato", choices=("texto", "json", "ambos"), default="ambos")
    parser.add_argument("--output", default="output")
    return parser


def configurar_logging(output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(filename=str(output / "painel.log"), level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", encoding="utf-8")


def executar(argv: list[str] | None = None) -> dict:
    args = configurar_argumentos().parse_args(argv)
    raiz = Path.cwd()

    alunos = args.alunos if Path(args.alunos).is_absolute() else raiz / args.alunos
    notas = args.notas if Path(args.notas).is_absolute() else raiz / args.notas
    config = args.config if Path(args.config).is_absolute() else raiz / args.config
    output = args.output if Path(args.output).is_absolute() else raiz / args.output

    configurar_logging(output)
    logger.info("Iniciando processamento do painel")
    resultado = processar(alunos, notas, config)

    if args.formato in ("texto", "ambos"):
        RelatorioTexto().gerar(resultado, output / "relatorio.txt")
    if args.formato in ("json", "ambos"):
        RelatorioJSON().gerar(resultado, output / "relatorio.json")

    logger.info("Processamento concluído: %s alunos", len(resultado["alunos"]))
    for erro in resultado["erros"]:
        logger.warning("%s", erro)

    if args.formato in ("texto", "ambos"):
        print((output / "relatorio.txt").read_text(encoding="utf-8"))
    else:
        print((output / "relatorio.json").read_text(encoding="utf-8"))
    return resultado


def main() -> None:
    executar()
