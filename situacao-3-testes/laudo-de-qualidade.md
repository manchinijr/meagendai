# Laudo de qualidade

**Sistema:** MeAgendaí · **Período de testes com usuários:** _(datas)_ · **Testadores:** 5

## 1. Resumo

| Indicador | Valor |
|---|---|
| Testes automatizados | 100 (100% aprovados) |
| Cobertura de código (Python) | 89% (regras de negócio: 100%) |
| Testadores externos | 5 |
| Defeitos relatados pelos testadores | _(preencher)_ |
| Defeitos corrigidos | _(preencher)_ |
| Sugestões implementadas | _(preencher)_ |
| Facilidade média para agendar (1–5) | _(preencher)_ |
| Satisfação média (1–5) | _(preencher)_ |

## 2. Critério de severidade

| Severidade | Definição | Prazo de correção |
|---|---|---|
| Alta | Impede uma funcionalidade principal (agendar, cancelar, entrar) ou causa perda/erro de dados | Antes da entrega |
| Média | A funcionalidade funciona, mas com erro visível ou comportamento confuso | Antes da entrega, se possível |
| Baixa | Cosmético ou sugestão de melhoria | Avaliar custo e benefício |

## 3. Defeitos e sugestões dos testadores

Cada item tem uma *issue* no GitHub (aba **Issues**) e aponta para o commit da correção.

| # | Testador | Descrição (o que aconteceu × o que era esperado) | Severidade | Evidência (print) | Decisão | Correção (issue / commit) | Verificado em |
|---|---|---|---|---|---|---|---|
| 1 | | | | | Corrigido / Não será corrigido (justificar) / Adiado | | |
| 2 | | | | | | | |
| 3 | | | | | | | |

## 4. Defeitos encontrados na verificação interna (antes dos testes com usuários)

| # | Origem | Descrição | Severidade | Correção | Evidência |
|---|---|---|---|---|---|
| I1 | Verificação visual (celular) | Após tocar em um horário, outro horário também parecia selecionado (hover preso em tela de toque) | Média | Destaque de hover desativado em telas de toque | Commit "Ajustes de interface…"; tela `ihc/telas/10-celular-agendar-horario.png` |
| I2 | Verificação visual (cadastro) | Mensagem de erro do aceite LGPD entre a caixa e o texto | Baixa | Mensagem movida para baixo do texto | Tela `ihc/telas/03-cadastro-validacao.png` |
| I3 | Revisão do painel | Linha do gráfico passava abaixo dos valores reais | Baixa | Interpolação monotônica | Tela `ihc/telas/16-painel.png` |
| I4 | Revisão da etapa de confirmação | Rolagem animada deslocava o botão "Confirmar" logo depois da escolha do horário | Média | Rolagem sem animação | Commit "Ajustes de interface…" |

## 5. Funcionalidades não testadas pelos usuários

| Funcionalidade | Motivo | Como foi coberta |
|---|---|---|
| _(preencher a partir das respostas)_ | | |

## 6. Conclusão

_(Preencher após as correções: o sistema atende aos requisitos? Quais defeitos ficaram em aberto e por quê?
Quais evoluções foram sugeridas para versões futuras?)_
