# Relatório dos testes automatizados

**Data da execução:** 27/10/2026 · **Versão:** commit atual da branch `main`
**Resultado:** ✅ **100 testes, 100 aprovados, 0 falhas**

| Nível | Ferramenta | Testes | Aprovados |
|---|---|---|---|
| Unitário (Python) | pytest | 23 | 23 |
| Unitário (JavaScript) | Vitest | 18 | 18 |
| Integração | pytest + PostgreSQL | 54 | 54 |
| Sistema (E2E) | Playwright | 5 | 5 |
| **Total** | | **100** | **100** |

A mesma suíte roda automaticamente no **GitHub Actions** a cada envio de código (aba *Actions* do repositório).

## Cobertura de código (Python)

| Módulo | Cobertura |
|---|---|
| `services/regras.py` (regras de negócio puras) | **100%** |
| `services/agendamento_service.py` | 91% |
| `services/cadastro_service.py` | 90% |
| `services/relatorio_service.py` | 90% |
| `services/config_service.py` | 90% |
| `services/disponibilidade_service.py` | 89% |
| `controllers/profissional.py` | 94% |
| `controllers/api.py` | 91% |
| `controllers/auth.py` | 87% |
| `controllers/cliente.py` | 82% |
| `controllers/admin.py` | 68% |
| `models/*` | 93% a 100% |
| **Total** | **89%** |

A meta do RNF06 (≥ 70% na camada `services`) foi atingida: todos os serviços estão entre 89% e 100%.
A menor cobertura está em `controllers/admin.py`, nos ramos de edição de profissional e de filtro de agendamentos,
que foram verificados manualmente e fazem parte do roteiro dos testadores.

## Defeitos encontrados pelos testes durante o desenvolvimento

| # | Teste que revelou | Defeito | Correção |
|---|---|---|---|
| 1 | `test_horario_agendado_some_da_lista` (E2E) | A expectativa do teste estava errada: um corte de 30 min às 09:45 colidiria com o horário das 10:00. O sistema estava certo | Teste corrigido para refletir a RN01 |
| 2 | Verificação visual das telas no celular | Destaque de hover "preso" depois de tocar em um horário | CSS com `@media (hover: none)` |
| 3 | Verificação visual do cadastro | Mensagem do aceite LGPD entre a caixa e o texto | Mensagem posicionada após o rótulo |
| 4 | Revisão do painel | Linha do gráfico passava abaixo dos valores reais | Interpolação monotônica |

## Exemplo de saída

```
$ pytest --cov=app
........................................................................ [ 87%]
..........                                                               [100%]
82 passed in 23.37s
TOTAL   1105   122   89%

$ npm test
 ✓ tests/js/validacoes.test.js (18 tests)
 Test Files  1 passed (1)
      Tests  18 passed (18)
```
