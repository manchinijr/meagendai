/* Comportamentos comuns: máscara de telefone, validação antes do envio e confirmações. */
document.addEventListener("DOMContentLoaded", function () {
  const V = window.Validacoes;

  document.querySelectorAll('[data-mascara="telefone"]').forEach(function (campo) {
    campo.addEventListener("input", function () {
      campo.value = V.mascaraTelefone(campo.value);
    });
  });

  function marcarErro(campo, mensagem) {
    campo.classList.add("is-invalid");
    let feedback = campo.parentElement.querySelector(".invalid-feedback");
    if (!feedback) {
      feedback = document.createElement("div");
      feedback.className = "invalid-feedback";
      // no checkbox a mensagem vai depois do rótulo, e não entre a caixa e o texto
      if (campo.type === "checkbox") campo.parentElement.appendChild(feedback);
      else campo.after(feedback);
    }
    feedback.textContent = mensagem;
  }

  document.querySelectorAll("form[data-validar]").forEach(function (form) {
    form.addEventListener("submit", function (evento) {
      let valido = true;
      form.querySelectorAll(".is-invalid").forEach(function (c) { c.classList.remove("is-invalid"); });

      form.querySelectorAll("input[required], textarea[required], select[required]").forEach(function (campo) {
        if (campo.type === "checkbox" ? !campo.checked : !campo.value.trim()) {
          marcarErro(campo, campo.type === "checkbox" ? "É preciso marcar esta opção." : "Campo obrigatório.");
          valido = false;
        }
      });
      form.querySelectorAll('input[type="email"]').forEach(function (campo) {
        if (campo.value && !V.emailValido(campo.value)) { marcarErro(campo, "E-mail inválido."); valido = false; }
      });
      form.querySelectorAll('[data-mascara="telefone"]').forEach(function (campo) {
        if (campo.value && !V.telefoneValido(campo.value)) {
          marcarErro(campo, "Informe um telefone válido, ex.: (11) 91234-5678.");
          valido = false;
        }
      });

      if (!valido) {
        evento.preventDefault();
        const primeiro = form.querySelector(".is-invalid");
        if (primeiro) primeiro.focus();
      } else {
        const botao = form.querySelector('button[type="submit"]');
        if (botao) { botao.disabled = true; botao.dataset.textoOriginal = botao.innerHTML; botao.innerHTML = "Enviando…"; }
      }
    });
  });

  document.querySelectorAll("form[data-confirmar]").forEach(function (form) {
    form.addEventListener("submit", function (evento) {
      if (!window.confirm(form.dataset.confirmar)) evento.preventDefault();
    });
  });

  const modalCancelar = document.getElementById("modal-cancelar");
  if (modalCancelar) {
    modalCancelar.addEventListener("show.bs.modal", function (evento) {
      const botao = evento.relatedTarget;
      modalCancelar.querySelector("form").action = botao.dataset.acao;
      modalCancelar.querySelector("[data-resumo]").textContent = botao.dataset.resumo;
    });
  }
});

/* Se o usuário voltar pelo navegador, reabilita botões desativados no envio. */
window.addEventListener("pageshow", function () {
  document.querySelectorAll("button[data-texto-original]").forEach(function (botao) {
    botao.disabled = false;
    botao.innerHTML = botao.dataset.textoOriginal;
  });
});
