from .entidades import Aluno, Nota


def calcular_medias_alunos(alunos: dict[int, Aluno], notas: list[Nota]) -> None:
    for aluno in alunos.values():
        aluno.notas = []
    for nota in notas:
        if nota.matricula in alunos:
            alunos[nota.matricula].notas.append(nota.valor)


def media_aluno(aluno: Aluno) -> float:
    return aluno.media()


def medias_por_disciplina(notas: list[Nota]) -> dict[str, float]:
    grupos: dict[str, list[float]] = {}
    for nota in notas:
        grupos.setdefault(nota.disciplina, []).append(nota.valor)

    medias: dict[str, float] = {}
    for disciplina in sorted(grupos):
        valores = grupos[disciplina]
        medias[disciplina] = sum(valores) / len(valores)
    return medias
