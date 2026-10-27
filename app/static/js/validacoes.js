/* Funções puras de validação e formatação, usadas nos formulários e testadas com Vitest. */
(function (raiz) {
  function apenasDigitos(texto) {
    return String(texto || "").replace(/\D/g, "");
  }

  function mascaraTelefone(texto) {
    const d = apenasDigitos(texto).slice(0, 11);
    if (d.length <= 2) return d.length ? "(" + d : "";
    if (d.length <= 6) return "(" + d.slice(0, 2) + ") " + d.slice(2);
    if (d.length <= 10) return "(" + d.slice(0, 2) + ") " + d.slice(2, 6) + "-" + d.slice(6);
    return "(" + d.slice(0, 2) + ") " + d.slice(2, 7) + "-" + d.slice(7);
  }

  function telefoneValido(texto) {
    const n = apenasDigitos(texto).length;
    return n === 10 || n === 11;
  }

  function emailValido(texto) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(String(texto || "").trim());
  }

  function senhaForte(texto) {
    const s = String(texto || "");
    return s.length >= 8 && /[A-Za-z]/.test(s) && /\d/.test(s);
  }

  function formatarDataBR(iso) {
    const [ano, mes, dia] = String(iso).slice(0, 10).split("-");
    return dia + "/" + mes + "/" + ano;
  }

  function formatarMoeda(valor) {
    return Number(valor || 0).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
  }

  const api = { apenasDigitos, mascaraTelefone, telefoneValido, emailValido, senhaForte, formatarDataBR, formatarMoeda };

  if (typeof module !== "undefined" && module.exports) {
    module.exports = api;
  } else {
    raiz.Validacoes = api;
  }
})(typeof window !== "undefined" ? window : globalThis);
