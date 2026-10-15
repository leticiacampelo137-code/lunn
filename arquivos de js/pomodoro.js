const start = document.getElementById("start");
const stop = document.getElementById("stop");
const reset = document.getElementById("reset");
const conometro = document.getElementById("conometro");
const jornadas = document.getElementById("jornadas");
const statusSessao = document.getElementById("status-sessao");
const urlSalvar = document.querySelector("main.pomodoro").dataset.saveUrl;
const csrfToken = document.querySelector("#csrf-pomodoro [name=csrfmiddlewaretoken]").value;

const TEMPO_ESTUDO = 25 * 60;
const TEMPO_DESCANSO = 5 * 60;

let tempoTotalRestante = 60 * 60;
let tempoAtual = TEMPO_ESTUDO;
let descansosRestantes = 2;
let intervalo = null;
let modoAtual = "estudo";
let segundosDeFoco = 0;
let salvandoSessao = false;

const updateTimer = () => {
    const minutos = Math.floor(tempoAtual / 60);
    const segundos = tempoAtual % 60;

    conometro.textContent = `${minutos.toString().padStart(2, "0")}:${segundos.toString().padStart(2, "0")}`;
};

const carregarJornada = () => {
    const optionSelecionada = jornadas.options[jornadas.selectedIndex];

    tempoTotalRestante = Number(optionSelecionada.value) * 60;
    descansosRestantes = Number(optionSelecionada.dataset.descansos);
    tempoAtual = TEMPO_ESTUDO;
    modoAtual = "estudo";

    updateTimer();
};

const salvarSessao = async (keepalive = false) => {
    if (segundosDeFoco <= 0 || salvandoSessao) {
        return;
    }

    const segundosParaSalvar = segundosDeFoco;
    segundosDeFoco = 0;
    salvandoSessao = true;
    const dados = new URLSearchParams({ segundos: String(segundosParaSalvar) });

    try {
        const resposta = await fetch(urlSalvar, {
            method: "POST",
            credentials: "same-origin",
            keepalive,
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRFToken": csrfToken
            },
            body: dados.toString()
        });

        if (!resposta.ok) {
            throw new Error("Falha ao salvar sessão.");
        }

        const minutosSalvos = Math.floor(segundosParaSalvar / 60);
        statusSessao.textContent = `Tempo registrado: ${minutosSalvos} min.`;
    } catch (erro) {
        segundosDeFoco += segundosParaSalvar;
        statusSessao.textContent = "Não foi possível salvar. Tente pausar novamente.";
    } finally {
        salvandoSessao = false;
    }
};

const trocarModo = () => {
    if (modoAtual === "estudo" && descansosRestantes > 0 && tempoTotalRestante > 0) {
        modoAtual = "descanso";
        descansosRestantes--;
        tempoAtual = TEMPO_DESCANSO;
    } else {
        modoAtual = "estudo";
        tempoAtual = TEMPO_ESTUDO;
    }
};

const startTimer = () => {
    clearInterval(intervalo);

    intervalo = setInterval(() => {
        tempoAtual--;
        tempoTotalRestante--;
        if (modoAtual === "estudo") {
            segundosDeFoco++;
        }
        updateTimer();

        if (tempoTotalRestante <= 0) {
            clearInterval(intervalo);
            intervalo = null;
            tempoAtual = 0;
            updateTimer();
            void salvarSessao();
            alert("Sessão finalizada");
            return;
        }

        if (tempoAtual <= 0) {
            trocarModo();
            updateTimer();
        }
    }, 1000);
};

const stopTimer = () => {
    clearInterval(intervalo);
    intervalo = null;
    void salvarSessao();
};

const resetTimer = () => {
    clearInterval(intervalo);
    intervalo = null;
    void salvarSessao();
    carregarJornada();
};

jornadas.addEventListener("change", resetTimer);
start.addEventListener("click", startTimer);
stop.addEventListener("click", stopTimer);
reset.addEventListener("click", resetTimer);
window.addEventListener("pagehide", () => {
    clearInterval(intervalo);
    void salvarSessao(true);
});

carregarJornada();
