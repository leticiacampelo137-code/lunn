const canvasPomodoro = document.getElementById("grafico-pomodoro");
const dadosPomodoro = document.getElementById("dados-pomodoro");

if (canvasPomodoro && dadosPomodoro && window.Chart) {
    const dados = JSON.parse(dadosPomodoro.textContent);
    const estilosTema = getComputedStyle(document.documentElement);
    const roxoLunar = estilosTema.getPropertyValue("--roxo-lunar").trim();
    const lilasSuave = estilosTema.getPropertyValue("--lilas-suave").trim();
    const roxoNoturno = estilosTema.getPropertyValue("--roxo-noturno").trim();

    new Chart(canvasPomodoro, {
        type: "bar",
        data: {
            labels: dados.map((dia) => dia.rotulo),
            datasets: [{
                data: dados.map((dia) => dia.minutos),
                backgroundColor: dados.map((_, indice) =>
                    indice === dados.length - 1 ? roxoLunar : lilasSuave
                ),
                borderRadius: 7,
                maxBarThickness: 42
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (contexto) => `${contexto.parsed.y} min de foco`
                    }
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: roxoNoturno }
                },
                y: {
                    beginAtZero: true,
                    suggestedMax: Math.max(30, Math.ceil(Math.max(...dados.map((dia) => dia.minutos)) / 15) * 15),
                    ticks: {
                        color: roxoNoturno,
                        callback: (valor) => `${valor} min`
                    },
                    grid: { color: lilasSuave }
                }
            }
        }
    });
}