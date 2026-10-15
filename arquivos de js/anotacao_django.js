const editor = document.getElementById("conteudo");
const formAnotacao = document.getElementById("form-anotacao");
const campoConteudo = document.getElementById("id_conteudo");
const conteudoInicial = document.getElementById("conteudo-inicial");
const barraEditor = document.querySelector(".barra-editor");
const fonteEditor = document.getElementById("fonte-editor");

document.querySelectorAll("[data-cor]").forEach((elemento) => {
    if (/^#[\da-f]{6}$/i.test(elemento.dataset.cor)) {
        elemento.style.backgroundColor = elemento.dataset.cor;
    }
});

if (editor && conteudoInicial) {
    editor.innerHTML = JSON.parse(conteudoInicial.textContent);
}

if (formAnotacao && editor && campoConteudo) {
    formAnotacao.addEventListener("submit", (evento) => {
        campoConteudo.value = editor.innerHTML;
        if (!editor.innerText.trim()) {
            evento.preventDefault();
            editor.setAttribute("aria-invalid", "true");
            editor.focus();
        }
    });
}

if (barraEditor && editor) {
    barraEditor.addEventListener("click", (evento) => {
        const botao = evento.target.closest("button[data-comando]");
        if (!botao) {
            return;
        }
        editor.focus();
        document.execCommand(botao.dataset.comando, false, botao.dataset.valor || null);
    });
}

if (fonteEditor && editor) {
    fonteEditor.addEventListener("change", () => {
        editor.focus();
        document.execCommand("fontName", false, fonteEditor.value);
    });
}

document.querySelectorAll("form[data-confirm]").forEach((formulario) => {
    formulario.addEventListener("submit", (evento) => {
        if (!window.confirm(formulario.dataset.confirm)) {
            evento.preventDefault();
        }
    });
});