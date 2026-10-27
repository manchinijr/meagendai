# Plano de testes

## 1. Objetivo
Garantir que o MeAgendaí faz o que foi especificado (**verificação**) e que atende às necessidades dos usuários
(**validação**), seguindo o **Modelo V** apresentado na disciplina.

| Lado esquerdo (especificação) | Nível de teste correspondente | Como é feito |
|---|---|---|
| Requisitos (`requisitos.md`) | **Teste de aceitação** | 5 testadores externos com formulário (`formulario-testadores.md`) |
| Análise (casos de uso, histórias) | **Teste de sistema** | Testes E2E automatizados no navegador (Playwright) |
| Arquitetura (MVC, serviços, banco) | **Teste de integração** | pytest + cliente de teste do Flask + PostgreSQL real |
| Código (funções) | **Teste unitário** | pytest (Python) e Vitest (JavaScript) |

## 2. Verificação × validação

| | Verificação ("construímos certo?") | Validação ("construímos a coisa certa?") |
|---|---|---|
| Quando | Durante o desenvolvimento | Após concluir os módulos |
| Atividades | Revisão dos requisitos com colegas (Kaizen), revisão de código, testes automatizados a cada envio (GitHub Actions) | Testes de aceitação com 5 usuários, coleta de bugs e sugestões |
| Evidências | `kaizen-feedback.md`, histórico de commits, execuções do CI, `relatorio-de-testes.md` | Avaliações em PDF e `laudo-de-qualidade.md` |

## 3. Escopo dos testes automatizados

| Nível | Ferramenta | Arquivo(s) | O que cobre |
|---|---|---|---|
| Unitário (Python) | pytest | `tests/unit/test_regras.py` | RN01 (sobreposição), RN02 (jornada, passado), RN03 (prazo, incluindo o limite exato), RN04 (bloqueio), RN05 (passo, serviço que não cabe), métricas do painel (incluindo divisão por zero e fuso horário) |
| Unitário (JavaScript) | Vitest | `tests/js/validacoes.test.js` | Máscara e validação de telefone, e-mail, senha, formatação de data e moeda |
| Integração | pytest + PostgreSQL | `tests/integration/test_agendamento_service.py` | Serviços com banco real: criação, conflito, constraint `EXCLUDE`, bloqueio por faltas, cancelamento, remarcação atômica, registro de atendimento, permissões |
| Integração | pytest + Flask test client | `tests/integration/test_rotas.py` | Rotas: login, cadastro, permissões por perfil, fluxo do cliente, API JSON, CRUD do administrador, configurações, CSRF, *open redirect*, hash de senha, 404 |
| Sistema (E2E) | Playwright (Chromium) | `tests/e2e/test_fluxos.py` | Fluxo completo de agendar e cancelar; horário reservado some da lista; validações no navegador; painel; agenda do profissional |

## 4. Técnicas usadas
- **Particionamento de equivalência e valor-limite:** ex.: cancelar com exatamente 2 h (permitido) e com 1 h 59 min
  (bloqueado); faltas = limite − 1 (libera) e = limite (bloqueia); serviço de 45 min que termina exatamente no fim da jornada.
- **Testes negativos:** dados inválidos, acessos de outro perfil, horário ocupado, período invertido no painel.
- **Tempo controlado:** as regras recebem o "agora" como parâmetro, o que torna os testes de horário determinísticos.
- **Banco real nos testes de integração:** o PostgreSQL é usado de verdade (e não SQLite), para validar as constraints.

## 5. Ambiente
- Local: Windows 11, Python 3.14, PostgreSQL 16 (Docker), Node 24.
- Integração contínua: GitHub Actions (Ubuntu, Python 3.13, PostgreSQL 16, Chromium, Node 22) a cada `push`.

## 6. Critérios de aceitação da entrega
- 100% dos testes automatizados passando no CI.
- Cobertura ≥ 70% na camada `services` (RNF06).
- Nenhum defeito de severidade **alta** em aberto após os testes com os usuários.
- Todos os defeitos encontrados registrados no laudo, com a correção ou a justificativa.

## 7. Como executar
```bash
docker compose up -d                       # PostgreSQL local
pip install -r requirements-dev.txt
python -m playwright install chromium      # uma vez
pytest --cov=app                           # Python: unitários, integração e E2E
npm install && npm test                    # JavaScript (Vitest)
```
