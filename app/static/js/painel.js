/* Painel do administrador (RF08): busca as métricas em /api/painel e desenha cartões e gráficos. */
document.addEventListener("DOMContentLoaded", function () {
  const V = window.Validacoes;
  const form = document.getElementById("filtro-painel");
  const caixaErro = document.getElementById("painel-erro");
  const cor = getComputedStyle(document.documentElement).getPropertyValue("--marca").trim() || "#4f46e5";
  let graficoDias = null;
  let graficoServicos = null;

  function escrever(id, texto) {
    document.getElementById("m-" + id).textContent = texto;
  }

  function desenhar(dados) {
    escrever("total", dados.total);
    escrever("taxa_faltas", dados.taxa_faltas.toLocaleString("pt-BR") + "%");
    escrever("faturamento_previsto", V.formatarMoeda(dados.faturamento_previsto));
    escrever("faturamento_realizado", V.formatarMoeda(dados.faturamento_realizado));

    const dias = Object.keys(dados.por_dia);
    if (graficoDias) graficoDias.destroy();
    graficoDias = new Chart(document.getElementById("grafico-dias"), {
      type: "line",
      data: {
        labels: dias.map(function (d) { return V.formatarDataBR(d).slice(0, 5); }),
        datasets: [{ label: "Agendamentos", data: Object.values(dados.por_dia), borderColor: cor, backgroundColor: cor + "33", fill: true, tension: 0.3 }],
      },
      options: { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { precision: 0 } } } },
    });

    if (graficoServicos) graficoServicos.destroy();
    graficoServicos = new Chart(document.getElementById("grafico-servicos"), {
      type: "bar",
      data: {
        labels: dados.top_servicos.map(function (s) { return s[0]; }),
        datasets: [{ label: "Agendamentos", data: dados.top_servicos.map(function (s) { return s[1]; }), backgroundColor: cor }],
      },
      options: { indexAxis: "y", plugins: { legend: { display: false } }, scales: { x: { beginAtZero: true, ticks: { precision: 0 } } } },
    });
  }

  async function carregar() {
    caixaErro.classList.add("d-none");
    const params = new URLSearchParams(new FormData(form));
    try {
      const resposta = await fetch(form.dataset.url + "?" + params.toString(), { headers: { Accept: "application/json" } });
      const dados = await resposta.json();
      if (!resposta.ok) throw new Error(dados.erro || "Erro ao carregar o painel.");
      desenhar(dados);
    } catch (erro) {
      caixaErro.textContent = erro.message || "Não foi possível carregar o painel.";
      caixaErro.classList.remove("d-none");
    }
  }

  form.addEventListener("submit", function (evento) {
    evento.preventDefault();
    carregar();
  });
  carregar();
});
