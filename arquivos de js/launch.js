document.querySelectorAll("[data-cor]").forEach((elemento) => {
    if (/^#[\da-f]{6}$/i.test(elemento.dataset.cor)) {
        elemento.style.backgroundColor = elemento.dataset.cor;
    }
});
