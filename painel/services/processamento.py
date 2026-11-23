from pathlib import Path

from ..core.entidades import Aluno, Nota
from ..core.metricas import calcular_medias_alunos, medias_por_disciplina
from ..core.validador import criar_erro, linha_vazia, validar_matricula, validar_nota
from ..infra.arquivos import ler_configuracao, ler_csv


def processar(alunos_path: str | Path, notas_path: str | Path, config_path: str | Path) -> dict:
    configuracao = ler_configuracao(config_path)
    erros = []
    alunos: dict[int, Aluno] = {}
    matriculas_cadastradas: set[int] = set()

    for linha, registro in ler_csv(alunos_path):
        campos = {chave: (valor or "").strip() for chave, valor in registro.items()}
        campo = linha_vazia(campos)
        if campo is not None:
            erros.append(criar_erro(Path(alunos_path).name, linha, f"campo vazio: {campo}"))
            continue

        matricula_texto = campos["matricula"]
        if not validar_matricula(matricula_texto):
            erros.append(criar_erro(Path(alunos_path).name, linha, f"matricula inválida ({matricula_texto})"))
            continue

        matricula = int(matricula_texto)
        if matricula in matriculas_cadastradas:
            erros.append(criar_erro(Path(alunos_path).name, linha, f"matrícula {matricula} já cadastrada"))
            continue

        matriculas_cadastradas.add(matricula)
        alunos[matricula] = Aluno(matricula, campos["nome"], campos["turma"])

    notas_validas: list[Nota] = []
    notas_invalidas = 0
    notas_chaves: set[tuple[int, str, str]] = set()

    for linha, registro in ler_csv(notas_path):
        campos = {chave: (valor or "").strip() for chave, valor in registro.items()}

        for campo in ("matricula", "disciplina", "avaliacao", "nota"):
            if not campos.get(campo):
                erros.append(criar_erro(Path(notas_path).name, linha, f"campo vazio: {campo}"))
                notas_invalidas += 1
                break
        else:
            matricula_texto = campos["matricula"]
            if not validar_matricula(matricula_texto):
                erros.append(criar_erro(Path(notas_path).name, linha, f"matricula inválida ({matricula_texto})"))
                notas_invalidas += 1
                continue

            matricula = int(matricula_texto)
            valor, erro_nota = validar_nota(campos["nota"], configuracao.nota_maxima)
            if erro_nota == "nota_invalida":
                erros.append(criar_erro(Path(notas_path).name, linha, f"nota inválida ('{campos['nota']}')"))
                notas_invalidas += 1
                continue
            if erro_nota == "nota_fora_do_intervalo":
                erros.append(criar_erro(Path(notas_path).name, linha, f"nota fora do intervalo ('{campos['nota']}')"))
                notas_invalidas += 1
                continue

            if matricula not in alunos:
                erros.append(criar_erro(Path(notas_path).name, linha, f"matrícula inexistente ({matricula})"))
                notas_invalidas += 1
                continue

            chave = (matricula, campos["disciplina"], campos["avaliacao"])
            if chave in notas_chaves:
                erros.append(criar_erro(Path(notas_path).name, linha, "avaliação duplicada " + "/".join(map(str, chave))))
                notas_invalidas += 1
                continue

            notas_chaves.add(chave)
            notas_validas.append(Nota(matricula, campos["disciplina"], campos["avaliacao"], valor))

    calcular_medias_alunos(alunos, notas_validas)
    return {
        "alunos": alunos,
        "notas_validas": len(notas_validas),
        "notas_invalidas": notas_invalidas,
        "erros": erros,
        "medias_disciplinas": medias_por_disciplina(notas_validas),
        "configuracao": configuracao,
    }
