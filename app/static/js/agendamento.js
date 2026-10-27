/* Etapa 3 do agendamento: busca os horários livres sem recarregar a página e monta a confirmação. */
document.addEventListener("DOMContentLoaded", function () {
  const V = window.Validacoes;
  const caixa = document.getElementById("horarios");
  const campoData = document.getElementById("data");
  const rotuloData = document.getElementById("data-rotulo");
  const formConfirmar = document.getElementById("form-confirmar");
  const campoInicio = document.getElementById("inicio");
  const resumo = document.getElementById("resumo");
  const dias = ["Domingo", "Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado"];

  function selecionar(botao) {
    caixa.querySelectorAll(".slot").forEach(function (b) { b.classList.remove("active"); b.setAttribute("aria-pressed", "false"); });
    botao.classList.add("active");
    botao.setAttribute("aria-pressed", "true");
    campoInicio.value = botao.dataset.inicio;
    resumo.textContent = V.formatarDataBR(campoData.value) + " às " + botao.textContent.trim();
    formConfirmar.classList.remove("d-none");
    formConfirmar.scrollIntoView({ block: "nearest" });
  }

  function mensagem(texto, classe) {
    caixa.innerHTML = "";
    const p = document.createElement("p");
    p.className = "mb-0 " + (classe || "text-muted");
    p.textContent = texto;
    caixa.appendChild(p);
  }

  function renderizar(horarios) {
    caixa.innerHTML = "";
    if (!horarios.length) {
      mensagem("Nenhum horário livre nesta data. Tente outro dia.");
      return;
    }
    horarios.forEach(function (h) {
      const botao = document.createElement("button");
      botao.type = "button";
      botao.className = "btn btn-outline-marca slot";
      botao.dataset.inicio = h.inicio;
      botao.textContent = h.rotulo;
      caixa.appendChild(botao);
    });
  }

  async function carregar() {
    formConfirmar.classList.add("d-none");
    campoInicio.value = "";
    const data = campoData.value;
    const dia = new Date(data + "T12:00:00");
    rotuloData.textContent = V.formatarDataBR(data) + " (" + dias[dia.getDay()] + ")";
    mensagem("Carregando horários…");

    const params = new URLSearchParams({ servico: caixa.dataset.servico, profissional: caixa.dataset.profissional, data: data });
    if (caixa.dataset.ignorar) params.set("ignorar", caixa.dataset.ignorar);
    try {
      const resposta = await fetch(caixa.dataset.url + "?" + params.toString(), { headers: { Accept: "application/json" } });
      if (!resposta.ok) throw new Error("HTTP " + resposta.status);
      const dados = await resposta.json();
      renderizar(dados.horarios);
    } catch (erro) {
      mensagem("Não foi possível carregar os horários. Verifique sua conexão e tente novamente.", "text-danger");
    }
  }

  caixa.addEventListener("click", function (evento) {
    const botao = evento.target.closest(".slot");
    if (botao) selecionar(botao);
  });
  campoData.addEventListener("change", function () {
    if (campoData.value) carregar();
  });
  formConfirmar.addEventListener("submit", function (evento) {
    if (!campoInicio.value) {
      evento.preventDefault();
      mensagem("Escolha um horário para continuar.", "text-danger");
    }
  });
});
