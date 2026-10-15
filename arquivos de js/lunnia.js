const form = document.getElementById("form-lunnia");
const campoMensagem = document.getElementById("mensagem");
const conversa = document.getElementById("conversa");
const status = document.getElementById("status-lunnia");
const botaoEnviar = form.querySelector("button[type='submit']");
const csrfToken = form.querySelector("[name=csrfmiddlewaretoken]").value;
const mensagens = [];

function adicionarMensagem(role, texto) {
    const mensagem = document.createElement("article");
    const autor = document.createElement("span");
    const conteudo = document.createElement("p");

    mensagem.className = `chat-message ${role === "user" ? "user-message" : "assistant-message"}`;
    autor.className = "message-author";
    autor.textContent = role === "user" ? "Você" : "LunnIA";
    conteudo.textContent = texto;
    mensagem.append(autor, conteudo);
    conversa.appendChild(mensagem);
    mensagem.scrollIntoView({ block: "nearest" });
}

form.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    const texto = campoMensagem.value.trim();
    if (!texto || botaoEnviar.disabled) return;

    mensagens.push({ role: "user", content: texto });
    adicionarMensagem("user", texto);
    campoMensagem.value = "";
    campoMensagem.style.height = "auto";
    botaoEnviar.disabled = true;
    status.textContent = "LunnIA está pensando…";

    try {
        const resposta = await fetch(form.dataset.endpoint, {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken
            },
            body: JSON.stringify({ messages: mensagens.slice(-12) })
        });
        const dados = await resposta.json();
        if (!resposta.ok) throw new Error(dados.erro || "Não foi possível obter uma resposta.");

        mensagens.push({ role: "assistant", content: dados.resposta });
        adicionarMensagem("assistant", dados.resposta);
        status.textContent = "";
    } catch (erro) {
        status.textContent = erro.message;
        mensagens.pop();
    } finally {
        botaoEnviar.disabled = false;
        campoMensagem.focus();
    }
});

campoMensagem.addEventListener("input", () => {
    campoMensagem.style.height = "auto";
    campoMensagem.style.height = `${Math.min(campoMensagem.scrollHeight, 150)}px`;
});

document.querySelectorAll("[data-sugestao]").forEach((botao) => {
    botao.addEventListener("click", () => {
        campoMensagem.value = botao.dataset.sugestao;
        campoMensagem.focus();
        campoMensagem.dispatchEvent(new Event("input"));
    });
});