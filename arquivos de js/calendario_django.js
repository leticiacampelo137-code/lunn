const grade = document.getElementById("grade-calendario");
const tituloMes = document.getElementById("mes-ano");
const tituloDia = document.getElementById("titulo-dia");
const listaEventos = document.getElementById("lista-eventos");
const formulario = document.getElementById("form-evento");
const statusCalendario = document.getElementById("status-calendario");
const materiasJson = document.getElementById("materias-calendario");
const eventosJson = document.getElementById("eventos-calendario");
const eventUrl = document.querySelector(".container-calendario").dataset.eventUrl;
const csrfToken = formulario.querySelector("[name=csrfmiddlewaretoken]").value;

const campoEventoId = document.getElementById("evento-id");
const campoTitulo = document.getElementById("evento-titulo");
const campoData = document.getElementById("evento-data");
const campoHorario = document.getElementById("evento-horario");
const campoTipo = document.getElementById("evento-tipo");
const campoMateria = document.getElementById("evento-materia");
const campoDescricao = document.getElementById("evento-descricao");
const tituloFormulario = document.getElementById("titulo-formulario");
const botaoSalvar = document.getElementById("salvar-evento");

const botaoAnterior = document.getElementById("mes-anterior");
const botaoProximo = document.getElementById("mes-proximo");
const botaoHoje = document.getElementById("mes-atual");
const botaoNovo = document.getElementById("novo-evento");
const botaoCancelar = document.getElementById("cancelar-evento");

const NOMES_MESES = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
];
const NOMES_DIAS = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"];
const TIPOS = {
    prova: "Prova",
    trabalho: "Trabalho",
    estudo: "Estudo",
    outro: "Outro"
};

let materias = JSON.parse(materiasJson.textContent);
let eventos = JSON.parse(eventosJson.textContent);
const hoje = dataLocal();
let dataSelecionada = hoje;
let anoVisivel = converterData(hoje).getFullYear();
let mesVisivel = converterData(hoje).getMonth();

function dataLocal(data = new Date()) {
    const ano = data.getFullYear();
    const mes = String(data.getMonth() + 1).padStart(2, "0");
    const dia = String(data.getDate()).padStart(2, "0");
    return `${ano}-${mes}-${dia}`;
}

function converterData(valor) {
    const [ano, mes, dia] = valor.split("-").map(Number);
    return new Date(ano, mes - 1, dia);
}

function formatarData(valor) {
    return converterData(valor).toLocaleDateString("pt-BR");
}

function anunciar(mensagem) {
    statusCalendario.textContent = mensagem;
}

function carregarMaterias() {
    campoMateria.replaceChildren(new Option("Sem matéria vinculada", ""));
    materias.forEach((materia) => {
        campoMateria.add(new Option(materia.nome, String(materia.id)));
    });
}

function renderizarCalendario() {
    grade.replaceChildren();
    tituloMes.textContent = `${NOMES_MESES[mesVisivel]} de ${anoVisivel}`;

    NOMES_DIAS.forEach((dia) => {
        const cabecalho = document.createElement("div");
        cabecalho.className = "cabecalho-semana";
        cabecalho.textContent = dia;
        grade.appendChild(cabecalho);
    });

    const primeiroDia = new Date(anoVisivel, mesVisivel, 1);
    const deslocamento = (primeiroDia.getDay() + 6) % 7;
    const inicio = new Date(anoVisivel, mesVisivel, 1 - deslocamento);

    for (let indice = 0; indice < 42; indice++) {
        const data = new Date(inicio);
        data.setDate(inicio.getDate() + indice);
        const valorData = dataLocal(data);
        const eventosDoDia = eventos.filter((evento) => evento.data === valorData);
        const botao = document.createElement("button");
        botao.type = "button";
        botao.className = "dia-calendario";
        botao.setAttribute("aria-pressed", String(valorData === dataSelecionada));
        botao.setAttribute("aria-label", `${formatarData(valorData)}, ${eventosDoDia.length} eventos`);

        if (data.getMonth() !== mesVisivel) botao.classList.add("fora-mes");
        if (valorData === hoje) botao.classList.add("hoje");
        if (valorData === dataSelecionada) botao.classList.add("selecionado");

        const numero = document.createElement("span");
        numero.className = "numero-dia";
        numero.textContent = data.getDate();
        const indicadores = document.createElement("span");
        indicadores.className = "indicadores-dia";
        indicadores.setAttribute("aria-hidden", "true");
        [...new Set(eventosDoDia.map((evento) => evento.tipo))].slice(0, 4).forEach((tipo) => {
            const ponto = document.createElement("i");
            ponto.className = `ponto ${TIPOS[tipo] ? tipo : "outro"}`;
            indicadores.appendChild(ponto);
        });

        botao.append(numero, indicadores);
        botao.addEventListener("click", () => {
            dataSelecionada = valorData;
            anoVisivel = data.getFullYear();
            mesVisivel = data.getMonth();
            renderizarCalendario();
            renderizarEventosDoDia();
        });
        grade.appendChild(botao);
    }
}

function renderizarEventosDoDia() {
    listaEventos.replaceChildren();
    tituloDia.textContent = `Eventos de ${formatarData(dataSelecionada)}`;
    const eventosDoDia = eventos
        .filter((evento) => evento.data === dataSelecionada)
        .sort((a, b) => (a.horario || "99:99").localeCompare(b.horario || "99:99"));

    if (!eventosDoDia.length) {
        const vazio = document.createElement("p");
        vazio.className = "evento-vazio";
        vazio.textContent = "Nenhum evento para este dia.";
        listaEventos.appendChild(vazio);
        return;
    }

    eventosDoDia.forEach((evento) => {
        const cartao = document.createElement("article");
        cartao.className = "evento-card";
        const conteudo = document.createElement("div");
        conteudo.className = "evento-conteudo";
        const tipo = document.createElement("span");
        tipo.className = "evento-tipo";
        tipo.textContent = TIPOS[evento.tipo] || TIPOS.outro;
        const titulo = document.createElement("h3");
        titulo.textContent = evento.titulo;
        conteudo.append(tipo, titulo);

        if (evento.horario) {
            const horario = document.createElement("p");
            horario.textContent = `Horário: ${evento.horario}`;
            conteudo.appendChild(horario);
        }
        if (evento.materiaNome) {
            const materia = document.createElement("p");
            materia.textContent = `Matéria: ${evento.materiaNome}`;
            conteudo.appendChild(materia);
        }
        if (evento.descricao) {
            const descricao = document.createElement("p");
            descricao.textContent = evento.descricao;
            conteudo.appendChild(descricao);
        }

        const acoes = document.createElement("div");
        acoes.className = "evento-acoes";
        const editar = document.createElement("button");
        editar.type = "button";
        editar.textContent = "Editar";
        editar.addEventListener("click", () => abrirFormulario(evento));
        const excluir = document.createElement("button");
        excluir.type = "button";
        excluir.textContent = "Excluir";
        excluir.addEventListener("click", () => excluirEvento(evento.id));
        acoes.append(editar, excluir);
        cartao.append(conteudo, acoes);
        listaEventos.appendChild(cartao);
    });
}

function abrirFormulario(evento = null) {
    formulario.reset();
    formulario.hidden = false;
    campoEventoId.value = evento?.id || "";
    tituloFormulario.textContent = evento ? "Editar evento" : "Adicionar evento";
    botaoSalvar.textContent = evento ? "Salvar alterações" : "Salvar evento";
    campoData.value = evento?.data || dataSelecionada;
    campoTitulo.value = evento?.titulo || "";
    campoHorario.value = evento?.horario || "";
    campoTipo.value = evento?.tipo || "estudo";
    campoMateria.value = evento?.materiaId ? String(evento.materiaId) : "";
    campoDescricao.value = evento?.descricao || "";
    campoTitulo.focus();
}

function fecharFormulario() {
    formulario.reset();
    formulario.hidden = true;
    campoEventoId.value = "";
}

async function enviarFormulario(dados) {
    const resposta = await fetch(eventUrl, {
        method: "POST",
        credentials: "same-origin",
        headers: { "X-CSRFToken": csrfToken },
        body: dados
    });
    const resultado = await resposta.json();
    if (!resposta.ok) {
        const erros = Object.values(resultado.erros || {}).flat().map((erro) => erro.message);
        throw new Error(erros[0] || "Não foi possível salvar o evento.");
    }
    return resultado;
}

formulario.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    const dados = new FormData(formulario);
    try {
        const salvo = await enviarFormulario(dados);
        const indice = eventos.findIndex((item) => item.id === salvo.id);
        if (indice === -1) eventos.push(salvo);
        else eventos[indice] = salvo;
        dataSelecionada = salvo.data;
        const dataEvento = converterData(salvo.data);
        anoVisivel = dataEvento.getFullYear();
        mesVisivel = dataEvento.getMonth();
        fecharFormulario();
        anunciar("Evento salvo.");
        renderizarCalendario();
        renderizarEventosDoDia();
    } catch (erro) {
        anunciar(erro.message);
    }
});

async function excluirEvento(id) {
    if (!window.confirm("Deseja excluir este evento?")) return;
    const dados = new FormData();
    dados.set("acao", "excluir");
    dados.set("evento_id", String(id));
    try {
        await enviarFormulario(dados);
        eventos = eventos.filter((evento) => evento.id !== id);
        anunciar("Evento excluído.");
        renderizarCalendario();
        renderizarEventosDoDia();
    } catch (erro) {
        anunciar(erro.message);
    }
}

botaoAnterior.addEventListener("click", () => {
    const data = new Date(anoVisivel, mesVisivel - 1, 1);
    anoVisivel = data.getFullYear();
    mesVisivel = data.getMonth();
    renderizarCalendario();
});

botaoProximo.addEventListener("click", () => {
    const data = new Date(anoVisivel, mesVisivel + 1, 1);
    anoVisivel = data.getFullYear();
    mesVisivel = data.getMonth();
    renderizarCalendario();
});

botaoHoje.addEventListener("click", () => {
    dataSelecionada = dataLocal();
    const data = converterData(dataSelecionada);
    anoVisivel = data.getFullYear();
    mesVisivel = data.getMonth();
    renderizarCalendario();
    renderizarEventosDoDia();
});

botaoNovo.addEventListener("click", () => abrirFormulario());
botaoCancelar.addEventListener("click", fecharFormulario);

carregarMaterias();
renderizarCalendario();
renderizarEventosDoDia();