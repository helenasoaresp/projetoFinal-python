from .entidades import ErroValidacao


def linha_vazia(registro: dict[str, str]) -> str | None:
    for campo in ("matricula", "nome", "turma"):
        if not (registro.get(campo) or "").strip():
            return campo
    return None


def validar_matricula(matricula: str) -> bool:
    return bool(matricula.strip()) and matricula.strip().isdigit()


def validar_nota(valor: str, nota_maxima: float) -> tuple[float | None, str | None]:
    texto = valor.strip()
    if not texto:
        return None, "campo_vazio"
    try:
        nota = float(texto)
    except ValueError:
        return None, "nota_invalida"
    if nota < 0 or nota > nota_maxima:
        return None, "nota_fora_do_intervalo"
    return nota, None


def criar_erro(arquivo: str, linha: int, mensagem: str) -> ErroValidacao:
    return ErroValidacao(arquivo=arquivo, linha=linha, mensagem=mensagem)
