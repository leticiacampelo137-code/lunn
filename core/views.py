import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from datetime import timedelta
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from urllib.parse import urlencode
from .forms import AnotacaoForm, EventoCalendarioForm, MateriaForm, TarefaForm, limpar_html_anotacao
from .models import Anotacao, EventoCalendario, Materia, SessaoPomodoro, Tarefa


def _redirect_anotacoes(materia_id=None, anotacao_id=None):
    parametros = []
    if materia_id is not None:
        parametros.append(("materia", str(materia_id)))
    if anotacao_id is not None:
        parametros.append(("anotacao", str(anotacao_id)))
    url = reverse("pagina_anotacoes")
    if parametros:
        url = f"{url}?{urlencode(parametros)}"
    return redirect(url)


def _resumo_pomodoro(usuario):
    hoje = timezone.localdate()
    dias = [hoje - timedelta(days=offset) for offset in range(6, -1, -1)]
    sessoes = SessaoPomodoro.objects.filter(
        usuario=usuario,
        dia__range=(dias[0], hoje),
    )
    segundos_por_dia = {dia: 0 for dia in dias}
    for sessao in sessoes:
        segundos_por_dia[sessao.dia] += sessao.duracao_segundos

    total_segundos = sum(segundos_por_dia.values())
    return {
        "grafico_pomodoro": [
            {
                "rotulo": dia.strftime("%d/%m"),
                "minutos": round(segundos_por_dia[dia] / 60, 1),
            }
            for dia in dias
        ],
        "total_minutos": round(total_segundos / 60),
        "total_sessoes": sessoes.count(),
    }


def _evento_calendario_json(evento):
    return {
        "id": evento.pk,
        "titulo": evento.titulo,
        "data": evento.data.isoformat(),
        "horario": evento.horario.strftime("%H:%M") if evento.horario else "",
        "tipo": evento.tipo,
        "materiaId": evento.materia_id,
        "materiaNome": evento.materia.nome if evento.materia else evento.materia_nome,
        "descricao": evento.descricao,
    }

def pagina_inicial(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        senha = request.POST.get("senha", "")
        user = authenticate(request, username=email, password=senha)
        if user is not None:
            login(request, user)
            return redirect("index")
        return render(request, "login.html", {"error": "E-mail ou senha inválidos."})
    return render(request, "login.html")

def pagina_cadastro(request):
    erro = None

    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        email = request.POST.get("email", "").strip().lower()
        senha = request.POST.get("senha", "")
        confirmar_senha = request.POST.get("confirmar-senha", "")
        Usuario = get_user_model()

        if senha != confirmar_senha:
            erro = "As senhas não coincidem."
        elif Usuario.objects.filter(email__iexact=email).exists():
            erro = "Este e-mail já está cadastrado."
        else:
            try:
                validate_password(senha)
            except ValidationError as exc:
                erro = " ".join(exc.messages)
            else:
                Usuario.objects.create_user(
                    username=email,
                    email=email,
                    password=senha,
                    first_name=nome,
                )
                return redirect("pagina_inicial")

    return render(request, "cadastro.html", {"error": erro})

@login_required(login_url="pagina_inicial")
def pagina_index(request):
    form = TarefaForm()
    materia_form = MateriaForm()
    editing_task_id = None
    hoje = timezone.localdate()

    if request.method == "POST":
        action = request.POST.get("acao", "criar")
        if action == "criar_materia":
            materia_form = MateriaForm(request.POST)
            if materia_form.is_valid():
                materia = materia_form.save(commit=False)
                materia.usuario = request.user
                materia.save()
                return redirect("index")
        elif action in {"alternar_status", "excluir", "editar"}:
            tarefa = get_object_or_404(
                Tarefa,
                pk=request.POST.get("tarefa_id"),
                usuario=request.user,
            )

            if action == "alternar_status":
                tarefa.completo = not tarefa.completo
                tarefa.save(update_fields=["completo"])
                return redirect("index")

            if action == "excluir":
                tarefa.delete()
                return redirect("index")

            form = TarefaForm(request.POST, instance=tarefa)
            if form.is_valid():
                form.save()
                return redirect("index")
            editing_task_id = tarefa.pk
        else:
            form = TarefaForm(request.POST)
            if form.is_valid():
                tarefa = form.save(commit=False)
                tarefa.usuario = request.user
                tarefa.save()
                return redirect("index")
    elif request.GET.get("editar"):
        tarefa = get_object_or_404(
            Tarefa,
            pk=request.GET["editar"],
            usuario=request.user,
        )
        form = TarefaForm(instance=tarefa)
        editing_task_id = tarefa.pk

    contexto = {
        "form": form,
        "tarefas": Tarefa.objects.filter(usuario=request.user).order_by("-data_criacao"),
        "editando": editing_task_id,
        "materia_form": materia_form,
        "materias": Materia.objects.filter(usuario=request.user),
        "eventos_semana": EventoCalendario.objects.filter(
            usuario=request.user,
            data__range=(hoje, hoje + timedelta(days=6)),
        ).select_related("materia").order_by("data", "horario", "titulo")[:5],
        "ultimas_anotacoes": Anotacao.objects.filter(
            materia__usuario=request.user,
        ).select_related("materia").order_by("-atualizada_em")[:3],
    }
    contexto.update(_resumo_pomodoro(request.user))
    return render(request, "index.html", contexto)

@login_required(login_url="pagina_inicial")
def pagina_calendario(request):
    materias = Materia.objects.filter(usuario=request.user).values("id", "nome")
    eventos = EventoCalendario.objects.filter(usuario=request.user).select_related("materia")
    contexto = {
        "materias_json": list(materias),
        "eventos_json": [_evento_calendario_json(evento) for evento in eventos],
    }
    return render(request, "calendario.html", contexto)


@login_required(login_url="pagina_inicial")
@require_POST
def salvar_evento_calendario(request):
    acao = request.POST.get("acao", "salvar")
    if acao == "excluir":
        evento = get_object_or_404(
            EventoCalendario,
            pk=request.POST.get("evento_id"),
            usuario=request.user,
        )
        evento.delete()
        return JsonResponse({"excluido": True})

    evento_id = request.POST.get("evento_id")
    instancia = None
    if evento_id:
        instancia = get_object_or_404(
            EventoCalendario,
            pk=evento_id,
            usuario=request.user,
        )

    form = EventoCalendarioForm(
        request.POST,
        instance=instancia,
        usuario=request.user,
    )
    if not form.is_valid():
        return JsonResponse({"erros": form.errors.get_json_data()}, status=400)

    evento = form.save(commit=False)
    evento.usuario = request.user
    evento.materia_nome = evento.materia.nome if evento.materia else ""
    evento.save()
    return JsonResponse(_evento_calendario_json(evento))



@login_required(login_url="pagina_inicial")
def pagina_lunnia(request):
    return render(request, "lunnia.html")
@login_required(login_url="pagina_inicial")
@require_POST
def responder_lunnia(request):
    try:
        dados = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"erro": "Mensagem inválida."}, status=400)

    mensagens_recebidas = dados.get("messages") if isinstance(dados, dict) else None

    if not isinstance(mensagens_recebidas, list):
        return JsonResponse({"erro": "Envie uma conversa válida."}, status=400)

    mensagens = []

    for item in mensagens_recebidas[-12:]:
        if not isinstance(item, dict):
            continue

        if item.get("role") not in {"user", "assistant"}:
            continue

        conteudo = item.get("content")

        if isinstance(conteudo, str) and conteudo.strip():
            mensagens.append({
                "role": item["role"],
                "content": conteudo.strip()[:3000],
            })

    if not mensagens or mensagens[-1]["role"] != "user":
        return JsonResponse(
            {"erro": "Escreva uma pergunta para a LunnIA."},
            status=400,
        )

    payload = json.dumps({
        "model": settings.LUNNIA_MODEL,
        "stream": False,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Você é a LunnIA, assistente de estudos do Lunn. "
                    "Responda em português brasileiro, com clareza e incentivo. "
                    "Ajude a organizar estudos, explicar conceitos e resolver "
                    "exercícios passo a passo. Não invente dados e sinalize "
                    "quando não tiver certeza."
                ),
            },
            *mensagens,
        ],
    }).encode("utf-8")

    requisicao = Request(
        settings.LUNNIA_API_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(requisicao, timeout=120) as resposta:
            resultado = json.loads(resposta.read().decode("utf-8"))

        texto = resultado["message"]["content"]

    except (
        HTTPError,
        URLError,
        TimeoutError,
        KeyError,
        TypeError,
        UnicodeDecodeError,
        json.JSONDecodeError,
    ):
        return JsonResponse(
            {
                "erro": (
                    "A LunnIA não conseguiu responder. "
                    "Verifique se o Ollama está aberto e tente novamente."
                )
            },
            status=502,
        )

    return JsonResponse({"resposta": texto})


@login_required(login_url="pagina_inicial")
def pagina_pomodoro(request):
    return render(request, "pomodoro.html")


@login_required(login_url="pagina_inicial")
@require_POST
def registrar_sessao_pomodoro(request):
    try:
        duracao_segundos = int(request.POST.get("segundos", ""))
    except (TypeError, ValueError):
        return JsonResponse({"erro": "Duração inválida."}, status=400)

    if not 0 < duracao_segundos <= 7200:
        return JsonResponse({"erro": "Duração fora do limite."}, status=400)

    sessao = SessaoPomodoro.objects.create(
        usuario=request.user,
        duracao_segundos=duracao_segundos,
        dia=timezone.localdate(),
    )
    return JsonResponse({"salvo": True, "id": sessao.pk})

@login_required(login_url="pagina_inicial")
def pagina_anotacoes(request):
    materias_usuario = Materia.objects.filter(usuario=request.user)
    materia_form = MateriaForm()
    materia_edicao_form = None
    anotacao_form = AnotacaoForm()
    materia_selecionada = None
    anotacao_selecionada = None
    materia_em_edicao = None

    if request.method == "POST":
        action = request.POST.get("acao")

        if action == "criar_materia":
            materia_form = MateriaForm(request.POST)
            if materia_form.is_valid():
                materia = materia_form.save(commit=False)
                materia.usuario = request.user
                materia.save()
                return _redirect_anotacoes(materia.pk)

        elif action == "editar_materia":
            materia_selecionada = get_object_or_404(
                materias_usuario,
                pk=request.POST.get("materia_id"),
            )
            materia_edicao_form = MateriaForm(request.POST, instance=materia_selecionada)
            if materia_edicao_form.is_valid():
                materia_edicao_form.save()
                return _redirect_anotacoes(materia_selecionada.pk)
            materia_em_edicao = materia_selecionada.pk

        elif action == "excluir_materia":
            materia = get_object_or_404(
                materias_usuario,
                pk=request.POST.get("materia_id"),
            )
            materia.delete()
            return redirect("pagina_anotacoes")

        elif action == "salvar_anotacao":
            materia_selecionada = get_object_or_404(
                materias_usuario,
                pk=request.POST.get("materia_id"),
            )
            anotacao_id = request.POST.get("anotacao_id")
            if anotacao_id:
                anotacao_selecionada = get_object_or_404(
                    Anotacao,
                    pk=anotacao_id,
                    materia=materia_selecionada,
                )
                anotacao_form = AnotacaoForm(
                    request.POST,
                    instance=anotacao_selecionada,
                )
            else:
                anotacao_form = AnotacaoForm(request.POST)

            if anotacao_form.is_valid():
                anotacao = anotacao_form.save(commit=False)
                anotacao.materia = materia_selecionada
                anotacao.save()
                return _redirect_anotacoes(materia_selecionada.pk, anotacao.pk)

        elif action == "excluir_anotacao":
            anotacao = get_object_or_404(
                Anotacao,
                pk=request.POST.get("anotacao_id"),
                materia__usuario=request.user,
            )
            materia_id = anotacao.materia_id
            anotacao.delete()
            return _redirect_anotacoes(materia_id)

    else:
        anotacao_id = request.GET.get("anotacao")
        if anotacao_id:
            anotacao_selecionada = get_object_or_404(
                Anotacao,
                pk=anotacao_id,
                materia__usuario=request.user,
            )
            materia_selecionada = anotacao_selecionada.materia
            anotacao_form = AnotacaoForm(instance=anotacao_selecionada)
        else:
            materia_id = request.GET.get("materia")
            if materia_id:
                materia_selecionada = get_object_or_404(
                    materias_usuario,
                    pk=materia_id,
                )

    if materia_selecionada is None:
        materia_selecionada = materias_usuario.first()

    contexto = {
        "materias": materias_usuario,
        "materia_form": materia_form,
        "materia_edicao_form": materia_edicao_form,
        "materia_selecionada": materia_selecionada,
        "materia_em_edicao": materia_em_edicao,
        "anotacoes": materia_selecionada.anotacoes.all() if materia_selecionada else [],
        "anotacao_form": anotacao_form,
        "anotacao_selecionada": anotacao_selecionada,
        "conteudo_inicial": limpar_html_anotacao(anotacao_form["conteudo"].value() or ""),
    }
    return render(request, "anotacoes.html", contexto)

