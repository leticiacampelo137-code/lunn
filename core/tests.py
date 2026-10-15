import json
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone

from .models import EventoCalendario, Materia


class EventoCalendarioTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.usuario = user_model.objects.create_user(
            username="estudante@example.com",
            email="estudante@example.com",
            password="senha-de-teste-123",
        )
        self.outro_usuario = user_model.objects.create_user(
            username="outra@example.com",
            email="outra@example.com",
            password="senha-de-teste-123",
        )
        self.materia = Materia.objects.create(
            usuario=self.usuario,
            nome="Matemática",
            cor="#7556D9",
        )
        self.client.force_login(self.usuario)
        self.url = "/calendario/eventos/"
        self.data = (timezone.localdate() + timedelta(days=1)).isoformat()

    def test_cria_edita_e_exclui_evento(self):
        dados = {
            "acao": "salvar",
            "titulo": "Revisão de cálculo",
            "data": self.data,
            "horario": "14:30",
            "tipo": "estudo",
            "materia": str(self.materia.pk),
            "descricao": "Limites e derivadas",
        }
        resposta = self.client.post(self.url, dados)
        evento = EventoCalendario.objects.get(usuario=self.usuario)

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(evento.materia, self.materia)
        self.assertEqual(evento.materia_nome, self.materia.nome)

        dados.update({
            "evento_id": str(evento.pk),
            "titulo": "Prova de cálculo",
            "tipo": "prova",
        })
        resposta = self.client.post(self.url, dados)
        evento.refresh_from_db()
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(evento.titulo, "Prova de cálculo")

        resposta = self.client.post(self.url, {
            "acao": "excluir",
            "evento_id": str(evento.pk),
        })
        self.assertEqual(resposta.status_code, 200)
        self.assertFalse(EventoCalendario.objects.filter(pk=evento.pk).exists())

    def test_evento_aparece_no_calendario_e_no_index_do_dono(self):
        evento = EventoCalendario.objects.create(
            usuario=self.usuario,
            materia=self.materia,
            materia_nome=self.materia.nome,
            titulo="Aula de revisão",
            data=timezone.localdate() + timedelta(days=1),
            tipo=EventoCalendario.Tipo.ESTUDO,
        )

        calendario = self.client.get("/calendario/")
        index = self.client.get("/index/")
        eventos_json = calendario.context["eventos_json"]

        self.assertEqual(calendario.status_code, 200)
        self.assertEqual(index.status_code, 200)
        self.assertEqual(eventos_json[0]["id"], evento.pk)
        self.assertContains(index, evento.titulo)

    def test_usuario_nao_acessa_eventos_ou_materias_de_outra_conta(self):
        evento = EventoCalendario.objects.create(
            usuario=self.usuario,
            materia=self.materia,
            titulo="Evento privado",
            data=timezone.localdate(),
            tipo=EventoCalendario.Tipo.ESTUDO,
        )
        materia_alheia = Materia.objects.create(
            usuario=self.outro_usuario,
            nome="Matéria privada",
            cor="#7556D9",
        )
        outro_cliente = self.client_class()
        outro_cliente.force_login(self.outro_usuario)

        resposta_evento = outro_cliente.post(self.url, {
            "acao": "salvar",
            "evento_id": str(evento.pk),
            "titulo": "Alteração indevida",
            "data": self.data,
            "tipo": "estudo",
        })
        resposta_materia = self.client.post(self.url, {
            "acao": "salvar",
            "titulo": "Matéria de outra conta",
            "data": self.data,
            "tipo": "estudo",
            "materia": str(materia_alheia.pk),
        })

        self.assertEqual(resposta_evento.status_code, 404)
        self.assertEqual(resposta_materia.status_code, 400)


class LunniaTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.usuario = user_model.objects.create_user(
            username="lunnia@example.com",
            email="lunnia@example.com",
            password="senha-de-teste-123",
        )
        self.client.force_login(self.usuario)

    @override_settings(LUNNIA_API_KEY="")
    def test_lunnia_page_opens_and_reports_missing_provider_key(self):
        pagina = self.client.get("/lunnia/")
        resposta = self.client.post(
            "/lunnia/responder/",
            data=json.dumps({"messages": [{"role": "user", "content": "Ajude-me a estudar."}]}),
            content_type="application/json",
        )

        self.assertEqual(pagina.status_code, 200)
        self.assertEqual(resposta.status_code, 503)
        self.assertIn("LUNNIA_API_KEY", resposta.json()["erro"])