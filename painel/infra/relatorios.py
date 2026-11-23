import json
from abc import ABC, abstractmethod
from pathlib import Path


class GeradorRelatorio(ABC):
    @abstractmethod
    def gerar(self, resultado: dict, caminho: str | Path) -> None:
        pass


class RelatorioTexto(GeradorRelatorio):
    def gerar(self, resultado: dict, caminho: str | Path) -> None:
        alunos = resultado["alunos"]
        erros = resultado["erros"]
        linhas = [
            "PAINEL DE NOTAS — RESUMO",
            f"Alunos processados: {len(alunos)}",
            f"Registros de nota válidos: {resultado['notas_validas']} | inválidos: {resultado['notas_invalidas']}",
            "",
            "Situação dos alunos",
        ]
        for aluno in sorted(alunos.values(), key=lambda item: item.nome):
            situacao = aluno.situacao(resultado["configuracao"].media_aprovacao, resultado["configuracao"].media_recuperacao)
            linhas.append(f"  {aluno.nome:<20} {aluno.turma:<3} média {aluno.media():.2f}  {situacao}")

        linhas.extend(["", "Média por disciplina"])
        for disciplina, media in resultado["medias_disciplinas"].items():
            linhas.append(f"  {disciplina:<12} {media:.2f}")

        linhas.extend(["", f"Erros encontrados ({len(erros)})"])
        for erro in erros:
            linhas.append(f"  {erro}")

        destino = Path(caminho)
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text("\n".join(linhas) + "\n", encoding="utf-8")


class RelatorioJSON(GeradorRelatorio):
    def gerar(self, resultado: dict, caminho: str | Path) -> None:
        alunos = []
        for aluno in sorted(resultado["alunos"].values(), key=lambda item: item.nome):
            alunos.append({
                "matricula": aluno.matricula,
                "nome": aluno.nome,
                "turma": aluno.turma,
                "media": round(aluno.media(), 2),
                "situacao": aluno.situacao(resultado["configuracao"].media_aprovacao, resultado["configuracao"].media_recuperacao),
            })

        dados = {
            "alunos_processados": len(alunos),
            "notas_validas": resultado["notas_validas"],
            "notas_invalidas": resultado["notas_invalidas"],
            "alunos": alunos,
            "medias_por_disciplina": {nome: round(media, 2) for nome, media in resultado["medias_disciplinas"].items()},
            "erros": [{"arquivo": erro.arquivo, "linha": erro.linha, "mensagem": erro.mensagem} for erro in resultado["erros"]],
        }
        destino = Path(caminho)
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
