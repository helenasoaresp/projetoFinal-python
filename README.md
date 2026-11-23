# Painel de Notas da Turma

Sistema em Python que consolida as notas de uma turma, valida dados incorretos, calcula médias e gera relatórios em texto e JSON.

## Objetivo

O programa lê `alunos.csv`, `notas.csv` e `config.json`, registra dados inválidos sem interromper o processamento, calcula a média de cada aluno e a média por disciplina e apresenta a situação acadêmica.

## Estrutura

```text
painel/
├── painel/
│   ├── __main__.py
│   ├── main.py
│   ├── core/
│   │   ├── entidades.py
│   │   ├── validador.py
│   │   └── metricas.py
│   ├── infra/
│   │   ├── arquivos.py
│   │   └── relatorios.py
│   └── services/
│       └── processamento.py
├── data/
├── tests/
└── README.md
```

- `core/entidades.py`: entidades `Aluno`, `Nota`, `Configuracao` e `ErroValidacao`.
- `core/validador.py`: validações de campos, matrículas e notas.
- `core/metricas.py`: médias dos alunos e das disciplinas.
- `infra/arquivos.py`: leitura dos CSV e JSON.
- `infra/relatorios.py`: relatórios abstrato, texto e JSON.
- `services/processamento.py`: coordenação do processamento.
- `main.py`: interface de linha de comando.
- `__main__.py`: execução como módulo.

## Formato dos arquivos

`alunos.csv` possui `matricula,nome,turma`. `notas.csv` possui `matricula,disciplina,avaliacao,nota`. `config.json` possui `media_aprovacao`, `media_recuperacao` e `nota_maxima`.

Espaços nas pontas são removidos. Campos vazios, matrículas inválidas ou duplicadas, notas inválidas ou fora do intervalo, matrículas inexistentes e avaliações duplicadas são registrados no relatório.

## Execução

Na raiz do projeto:

```bash
python -m painel --alunos data/alunos.csv --notas data/notas.csv --config data/config.json --formato ambos --output output/
```

Os formatos disponíveis são `texto`, `json` e `ambos`. Os arquivos são criados em `output/relatorio.txt`, `output/relatorio.json` e `output/painel.log`.

## Testes

```bash
python -m unittest discover -s tests
```
