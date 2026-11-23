from dataclasses import dataclass, field


@dataclass
class Aluno:
    matricula: int
    nome: str
    turma: str
    notas: list[float] = field(default_factory=list)

    def media(self) -> float:
        if not self.notas:
            return 0.0
        return sum(self.notas) / len(self.notas)

    def situacao(self, media_aprovacao: float, media_recuperacao: float) -> str:
        media = self.media()
        if media >= media_aprovacao:
            return "aprovado"
        if media >= media_recuperacao:
            return "recuperação"
        return "reprovado"


@dataclass
class Nota:
    matricula: int
    disciplina: str
    avaliacao: str
    valor: float


@dataclass
class Configuracao:
    media_aprovacao: float
    media_recuperacao: float
    nota_maxima: float


@dataclass
class ErroValidacao:
    arquivo: str
    linha: int
    mensagem: str

    def __str__(self) -> str:
        return f"{self.arquivo}:{self.linha} {self.mensagem}"
