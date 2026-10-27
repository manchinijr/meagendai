import { createRequire } from "node:module";
import { describe, expect, it } from "vitest";

const require = createRequire(import.meta.url);
const V = require("../../app/static/js/validacoes.js");

describe("mascaraTelefone", () => {
  it("formata celular com 11 dígitos", () => {
    expect(V.mascaraTelefone("11912345678")).toBe("(11) 91234-5678");
  });

  it("formata fixo com 10 dígitos", () => {
    expect(V.mascaraTelefone("1132345678")).toBe("(11) 3234-5678");
  });

  it("ignora letras e símbolos digitados", () => {
    expect(V.mascaraTelefone("11 a9-1234.5678")).toBe("(11) 91234-5678");
  });

  it("formata enquanto o usuário digita", () => {
    expect(V.mascaraTelefone("1")).toBe("(1");
    expect(V.mascaraTelefone("119")).toBe("(11) 9");
  });

  it("corta dígitos excedentes", () => {
    expect(V.mascaraTelefone("119123456789999")).toBe("(11) 91234-5678");
  });

  it("devolve vazio para entrada vazia", () => {
    expect(V.mascaraTelefone("")).toBe("");
    expect(V.mascaraTelefone(null)).toBe("");
  });
});

describe("telefoneValido", () => {
  it.each([
    ["(11) 91234-5678", true],
    ["(11) 3234-5678", true],
    ["(11) 9123", false],
    ["", false],
  ])("%s → %s", (entrada, esperado) => {
    expect(V.telefoneValido(entrada)).toBe(esperado);
  });
});

describe("emailValido", () => {
  it.each([
    ["cliente@meagendai.com", true],
    ["  com.espacos@exemplo.com.br  ", true],
    ["sem-arroba.com", false],
    ["a@b", false],
    ["a b@c.com", false],
  ])("%s → %s", (entrada, esperado) => {
    expect(V.emailValido(entrada)).toBe(esperado);
  });
});

describe("senhaForte", () => {
  it("exige 8 caracteres com letras e números", () => {
    expect(V.senhaForte("Senha123")).toBe(true);
    expect(V.senhaForte("Sen123")).toBe(false);
    expect(V.senhaForte("somenteletras")).toBe(false);
    expect(V.senhaForte("12345678")).toBe(false);
  });
});

describe("formatação", () => {
  it("converte data ISO para o padrão brasileiro", () => {
    expect(V.formatarDataBR("2026-11-05")).toBe("05/11/2026");
    expect(V.formatarDataBR("2026-11-05T10:00:00-03:00")).toBe("05/11/2026");
  });

  it("formata valores em reais", () => {
    expect(V.formatarMoeda(1234.5).replace(/\s/g, " ")).toBe("R$ 1.234,50");
    expect(V.formatarMoeda(0).replace(/\s/g, " ")).toBe("R$ 0,00");
  });
});
