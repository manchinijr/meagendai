# Formulário de avaliação para os testadores

**Link do formulário:** _(link do Google Forms)_
**Endereço do sistema:** _(link do sistema publicado)_

O formulário foi montado no Google Forms (com envio de imagens) e segue o modelo mínimo pedido no enunciado:
nome, data, o que funcionou, o que não funcionou (e o que corrigir) e funcionalidades não testadas, com motivo.

## Mensagem de convite

> Olá! Estou desenvolvendo o **MeAgendaí**, um sistema de agendamento online, para o Projeto Integrador de Engenharia
> de Software. Você pode me ajudar testando o sistema por uns 15 minutos?
>
> 1. Acesse: _(link do sistema)_. O primeiro acesso pode demorar até 1 minuto para carregar.
> 2. Siga o roteiro abaixo (crie sua própria conta de cliente e use também as contas de demonstração).
> 3. Preencha o formulário: _(link do formulário)_. Se algo der errado, **tire um print da tela** e anexe.
>
> Pode ser bem sincero(a): os erros que você encontrar vão me ajudar a melhorar o sistema. Obrigado!

## Roteiro sugerido de testes

| # | Como cliente (crie uma conta nova) | Resultado esperado |
|---|---|---|
| 1 | Criar conta deixando campos em branco e com e-mail inválido | Mensagens de erro em cada campo |
| 2 | Criar conta com dados válidos | Entra no sistema automaticamente |
| 3 | Agendar um serviço para um dia útil | Mensagem de confirmação e o horário aparece em "Meus agendamentos" |
| 4 | Voltar ao mesmo serviço, profissional e data | O horário reservado (e os que colidem com ele) não aparecem mais |
| 5 | Remarcar o agendamento | O horário muda |
| 6 | Cancelar o agendamento | Pede confirmação e depois mostra "Agendamento cancelado." |
| 7 | Tentar abrir o endereço `/admin` | Página "Acesso negado" |
| 8 | Usar o sistema pelo celular | As telas se ajustam à tela pequena |

| # | Como profissional (carlos@meagendai.com / Prof@1234) | Resultado esperado |
|---|---|---|
| 9 | Ver a agenda do dia e da semana | Lista os atendimentos |
| 10 | Marcar um atendimento passado como "Realizado" ou "Faltou" | Status atualizado |

| # | Como administrador (admin@meagendai.com / Admin@123) | Resultado esperado |
|---|---|---|
| 11 | Ver o painel e mudar o período | Indicadores e gráficos atualizam |
| 12 | Cadastrar um serviço novo | Aparece na página inicial |
| 13 | Cadastrar um profissional e a jornada dele | Ele passa a aparecer no agendamento do serviço |
| 14 | Mudar a antecedência de cancelamento em Configurações | A nova regra passa a valer |

## Perguntas do formulário

| # | Pergunta | Tipo | Obrigatória |
|---|---|---|---|
| 1 | Nome de quem testou | Resposta curta | Sim |
| 2 | Data do teste | Data | Sim |
| 3 | Perfil / ocupação (colega de curso, profissional da área etc.) | Resposta curta | Não |
| 4 | Dispositivo e navegador usados (ex.: celular Android / Chrome) | Resposta curta | Sim |
| 5 | Quais itens do roteiro você testou? | Caixas de seleção (itens 1 a 14) | Sim |
| 6 | **O que testou e funcionou** (descreva as funcionalidades) | Parágrafo | Sim |
| 7 | **O que testou e não funcionou**: o que aconteceu e o que deveria acontecer (o que deve ser corrigido) | Parágrafo | Sim (escreva "nada" se tudo funcionou) |
| 8 | Prints das telas com erro | Envio de arquivo (imagens) | Não |
| 9 | **Funcionalidades não testadas** e por quê (faltou tempo, não encontrou, não existe etc.) | Parágrafo | Sim |
| 10 | Sugestões de melhoria | Parágrafo | Não |
| 11 | De 1 a 5, quão fácil foi agendar um horário? | Escala linear 1–5 | Sim |
| 12 | De 1 a 5, qual sua satisfação geral com o sistema? | Escala linear 1–5 | Sim |

## Geração do PDF com as avaliações

1. No Google Forms, aba **Respostas → Individual**: imprima cada resposta em PDF (Ctrl + P → Salvar como PDF),
   ou use o modelo [`modelo-avaliacao.md`](modelo-avaliacao.md) para consolidar as cinco respostas.
2. Junte as cinco avaliações (com os prints anexados) em um único arquivo: `avaliacoes-testadores.pdf`.
3. Copie o resumo de cada avaliação para a tabela "Testes da Solução" do documento de entrega.
