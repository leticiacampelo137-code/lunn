from django.conf import settings
from django.db import models
from django.utils import timezone

class User_cadastro(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField()
    senha = models.CharField(max_length=100)

    def __str__(self):
        return self.nome #se a gente quiser ver o nome do usuario no admin, a gente coloca isso aqui


class Tarefa(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tarefas",
    )
    nome = models.CharField(max_length=100)
    descricao = models.TextField(null=True, blank=True)
    completo = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome


class Materia(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="materias",
    )
    nome = models.CharField(max_length=40)
    cor = models.CharField(max_length=7, default="#7556D9")
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Anotacao(models.Model):
    materia = models.ForeignKey(
        Materia,
        on_delete=models.CASCADE,
        related_name="anotacoes",
    )
    titulo = models.CharField(max_length=160)
    conteudo = models.TextField()
    criada_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-atualizada_em"]

    def __str__(self):
        return self.titulo


class SessaoPomodoro(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sessoes_pomodoro",
    )
    duracao_segundos = models.PositiveIntegerField()
    dia = models.DateField(default=timezone.localdate)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criada_em"]

    def __str__(self):
        return f"{self.usuario} - {self.duracao_segundos}s"


class EventoCalendario(models.Model):
    class Tipo(models.TextChoices):
        PROVA = "prova", "Prova"
        TRABALHO = "trabalho", "Trabalho"
        ESTUDO = "estudo", "Estudo"
        OUTRO = "outro", "Outro"

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="eventos_calendario",
    )
    materia = models.ForeignKey(
        Materia,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="eventos",
    )
    materia_nome = models.CharField(max_length=40, blank=True)
    titulo = models.CharField(max_length=100)
    data = models.DateField()
    horario = models.TimeField(null=True, blank=True)
    tipo = models.CharField(max_length=12, choices=Tipo.choices, default=Tipo.OUTRO)
    descricao = models.TextField(blank=True)
    criada_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["data", "horario", "titulo"]

    def __str__(self):
        return f"{self.titulo} ({self.data:%d/%m/%Y})"