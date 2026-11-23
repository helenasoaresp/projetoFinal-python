import json
import tempfile
import unittest
from pathlib import Path

from painel.core.entidades import Aluno, Nota, Configuracao
from painel.core.metricas import medias_por_disciplina
from painel.core.validador import validar_matricula, validar_nota
from painel.infra.arquivos import ler_configuracao, ler_csv
from painel.infra.relatorios import RelatorioJSON, RelatorioTexto
from painel.services.processamento import processar


class TestEntidades(unittest.TestCase):
    def test_aluno_calcula_media_e_situacao(self):
        aluno = Aluno(1001, "Ana", "3A", [8.0, 6.0])
        self.assertEqual(aluno.media(), 7.0)
        self.assertEqual(aluno.situacao(6.0, 4.0), "aprovado")

    def test_nota_e_configuracao(self):
        nota = Nota(1001, "Matemática", "P1", 8.5)
        config = Configuracao(6.0, 4.0, 10.0)
        self.assertEqual(nota.valor, 8.5)
        self.assertEqual(config.nota_maxima, 10.0)


class TestValidacaoMetricas(unittest.TestCase):
    def test_matricula_e_nota(self):
        self.assertTrue(validar_matricula("1001"))
        self.assertFalse(validar_matricula("10x1"))
        self.assertEqual(validar_nota("8.5", 10.0), (8.5, None))
        self.assertEqual(validar_nota("11", 10.0)[1], "nota_fora_do_intervalo")
        self.assertEqual(validar_nota("oito", 10.0)[1], "nota_invalida")

    def test_medias_por_disciplina(self):
        notas = [Nota(1, "Matemática", "P1", 8.0), Nota(2, "Matemática", "P1", 6.0), Nota(1, "Física", "P1", 7.0)]
        medias = medias_por_disciplina(notas)
        self.assertEqual(medias["Matemática"], 7.0)
        self.assertEqual(medias["Física"], 7.0)


class TestArquivos(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_leitura_csv_e_configuracao(self):
        alunos = self.base / "alunos.csv"
        config = self.base / "config.json"
        alunos.write_text("matricula,nome,turma\n1001,Ana,3A\n", encoding="utf-8")
        config.write_text('{"media_aprovacao":6,"media_recuperacao":4,"nota_maxima":10}', encoding="utf-8")

        registros = ler_csv(alunos)
        configuracao = ler_configuracao(config)
        self.assertEqual(registros[0][0], 2)
        self.assertEqual(registros[0][1]["nome"], "Ana")
        self.assertEqual(configuracao.nota_maxima, 10.0)


class TestRelatorios(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        aluno = Aluno(1001, "Ana Souza", "3A", [8.0])
        self.resultado = {
            "alunos": {1001: aluno}, "notas_validas": 1, "notas_invalidas": 1,
            "erros": [], "medias_disciplinas": {"Matemática": 8.0},
            "configuracao": Configuracao(6.0, 4.0, 10.0),
        }

    def tearDown(self):
        self.tmp.cleanup()

    def test_gera_texto_e_json(self):
        texto = self.base / "relatorio.txt"
        json_saida = self.base / "relatorio.json"
        RelatorioTexto().gerar(self.resultado, texto)
        RelatorioJSON().gerar(self.resultado, json_saida)
        self.assertIn("Ana Souza", texto.read_text(encoding="utf-8"))
        dados = json.loads(json_saida.read_text(encoding="utf-8"))
        self.assertEqual(dados["alunos"][0]["situacao"], "aprovado")


class TestProcessamentoIntegrado(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        (self.base / "alunos.csv").write_text(
            "matricula,nome,turma\n1001,Ana,3A\n1001,Ana duplicada,3A\n10x2,Bia,3B\n,Sem nome,3A\n",
            encoding="utf-8",
        )
        (self.base / "notas.csv").write_text(
            "matricula,disciplina,avaliacao,nota\n1001,Matemática,P1,8\n1001,Matemática,P1,9\n9999,Matemática,P1,7\n1001,Física,P1,oito\n1001,História,P1,11\n",
            encoding="utf-8",
        )
        (self.base / "config.json").write_text(
            '{"media_aprovacao":6,"media_recuperacao":4,"nota_maxima":10}', encoding="utf-8"
        )

    def tearDown(self):
        self.tmp.cleanup()

    def test_processa_invalidos_sem_interrupcao(self):
        resultado = processar(
            self.base / "alunos.csv", self.base / "notas.csv", self.base / "config.json"
        )
        self.assertEqual(len(resultado["alunos"]), 1)
        self.assertEqual(resultado["notas_validas"], 1)
        self.assertEqual(resultado["notas_invalidas"], 4)
        self.assertGreaterEqual(len(resultado["erros"]), 7)


if __name__ == "__main__":
    unittest.main()
