# Melhoria contínua (Kaizen): revisão do planejamento pelos colegas

O planejamento (escopo, requisitos, UML, telas e banco de dados) foi apresentado a colegas do curso para receber
críticas antes e durante o desenvolvimento. Cada sugestão foi avaliada e registrada abaixo, com a decisão tomada.

> Observação: este projeto foi planejado do zero nesta disciplina, porque os documentos do Projeto Integrador I não
> estavam mais disponíveis. Por isso, a revisão parte do planejamento atual.

## Registro das revisões

| # | Revisor(a) | Data | Artefato revisado | Sugestão / crítica | Decisão | O que mudou |
|---|---|---|---|---|---|---|
| 1 | | | | | Aceita / Recusada / Adiada | |
| 2 | | | | | | |
| 3 | | | | | | |

## Melhorias identificadas pelo próprio autor durante o desenvolvimento

| # | Data | Problema percebido | Melhoria aplicada |
|---|---|---|---|
| 1 | 27/10/2026 | No celular, o destaque de "passar o mouse" ficava preso em um horário depois do toque, parecendo que dois horários estavam selecionados | Destaque de hover desativado em telas de toque; só o horário escolhido fica marcado |
| 2 | 27/10/2026 | A mensagem de erro do aceite LGPD aparecia entre a caixa de seleção e o texto | Mensagem movida para baixo do texto do aceite |
| 3 | 27/10/2026 | O gráfico de agendamentos por dia "curvava" abaixo dos valores reais entre dois pontos | Interpolação monotônica, sem ultrapassar os valores reais |
| 4 | 27/10/2026 | A rolagem animada até o resumo fazia o botão "Confirmar" mudar de lugar logo após a escolha do horário | Rolagem sem animação |
| 5 | 27/10/2026 | A remarcação poderia deixar o cliente sem horário se o novo estivesse ocupado | Remarcação feita em uma única transação: se o novo horário falhar, o antigo continua valendo |
