# IHC: Interface Humano-Computador

## 1. Princípios aplicados

Os princípios de interface do material da disciplina (USABILITY.GOV, 2020) foram aplicados assim:

| Princípio | Como aparece no MeAgendaí |
|---|---|
| **Clara** | Agendamento dividido em 3 passos numerados (Serviço → Profissional → Horário), com indicação do passo atual |
| **Consistente** | Mesma barra de navegação, mesmas cores (botão principal sempre roxo) e os mesmos componentes do Bootstrap em todas as telas |
| **Simples** | O cliente só vê horários realmente livres, sem precisar interpretar uma agenda cheia |
| **Controlada pelo usuário** | Nada é confirmado sem o clique em "Confirmar"; há botões "Voltar" e "Trocar serviço" |
| **Direta** | Ao tocar em um horário, o resumo da reserva aparece logo abaixo |
| **Recuperável / reversível** | Cancelamento com janela de confirmação ("Manter" ou "Sim, cancelar"); remarcação que não perde o horário antigo se o novo falhar |
| **Dá resposta (feedback)** | Mensagens de sucesso e de erro após cada ação; "Carregando horários…"; botão muda para "Enviando…" para evitar duplo envio |
| **Esteticamente agradável** | Paleta reduzida, espaçamento generoso, cartões e ícones |
| **Comunica o estado** | Status do agendamento com cores (Agendado, Realizado, Faltou, Cancelado); aviso de bloqueio por faltas |
| **Pense nos padrões** | A data já vem preenchida com o dia atual; horários no formato brasileiro; máscara automática de telefone |
| **Acessibilidade** | Rótulos em todos os campos, `aria-live` na lista de horários, link "Pular para o conteúdo", navegação por teclado |
| **Responsiva** | Layout adaptado para celular (ver telas 10 e 11) |

## 2. Mapa de navegação

![Mapa de telas](mapa-de-telas.png)

## 3. Catálogo de mensagens

| Código | Situação | Mensagem exibida | Tipo |
|---|---|---|---|
| E01 | Login com e-mail ou senha errados | E-mail ou senha incorretos. | Erro |
| E02 | Cadastro com e-mail já usado | Este e-mail já possui cadastro. Deseja entrar? | Erro (no campo) |
| E03 | Horário reservado por outra pessoa (RN01) | Esse horário acabou de ser reservado. Escolha outro horário disponível. | Erro |
| E04 | Horário no passado (RN02) | Não é possível agendar em um horário que já passou. | Erro |
| E05 | Fora da jornada (RN02) | O profissional não atende nesse horário. | Erro |
| E06 | Cancelamento fora do prazo (RN03) | Cancelamentos e remarcações são permitidos até {N} h antes do horário. | Erro |
| E07 | Cliente bloqueado (RN04) | Seu agendamento online está bloqueado por faltas. Entre em contato com o estabelecimento. | Aviso |
| E08 | Acesso a página de outro perfil (403) | Você não tem permissão para acessar esta página. | Página de erro |
| E09 | Página inexistente (404) | O endereço acessado não existe ou foi removido. | Página de erro |
| E10 | Erro inesperado (500) | Algo deu errado do nosso lado. Tente novamente em instantes. | Página de erro |
| E11 | Sessão/formulário expirado (CSRF) | Sua sessão expirou. Recarregue a página e tente novamente. | Página de erro |
| E12 | Serviço com nome repetido | Já existe um serviço com esse nome. | Erro (no campo) |
| E13 | Jornada sobreposta (RN08) | Esse período se sobrepõe a outra jornada do mesmo dia. | Erro |
| E14 | Registrar atendimento antes do horário | Só é possível registrar o atendimento depois do horário de início. | Erro |
| E15 | Falha ao carregar horários | Não foi possível carregar os horários. Verifique sua conexão e tente novamente. | Erro |
| E16 | Período inválido no painel | A data final deve ser igual ou posterior à inicial. | Erro |
| V01 | Campo obrigatório vazio | Campo obrigatório. | Validação |
| V02 | E-mail com formato inválido | E-mail inválido. | Validação |
| V03 | Telefone inválido | Informe um telefone válido, ex.: (11) 91234-5678. | Validação |
| V04 | Senha fraca | A senha deve ter pelo menos 8 caracteres, com letras e números. | Validação |
| V05 | Senhas diferentes | As senhas não conferem. | Validação |
| V06 | Aceite LGPD não marcado | É preciso aceitar os termos para criar a conta. | Validação |
| S01 | Agendamento criado | Agendamento confirmado para {data} às {hora} com {profissional}. | Sucesso |
| S02 | Agendamento cancelado | Agendamento cancelado. | Sucesso |
| S03 | Remarcação feita | Agendamento remarcado para {data} às {hora}. | Sucesso |
| S04 | Atendimento registrado | Atendimento marcado como {realizado/faltou}. | Sucesso |
| S05 | Faltas zeradas | Faltas de {cliente} zeradas. O agendamento online foi liberado. | Sucesso |

## 4. Telas (protótipo funcional)

O protótipo foi evoluído diretamente para telas funcionais em HTML, CSS e JavaScript (Bootstrap 5). As capturas
abaixo são do sistema em execução com os dados de demonstração.

### Visitante e cliente
| | |
|---|---|
| ![Início](telas/01-inicio.png) Início | ![Login](telas/02-login.png) Login |
| ![Cadastro](telas/03-cadastro-validacao.png) Cadastro com validações | ![Passo 1](telas/04-agendar-servico.png) Passo 1: serviço |
| ![Passo 2](telas/05-agendar-profissional.png) Passo 2: profissional | ![Passo 3](telas/06-agendar-horario.png) Passo 3: horário e confirmação |
| ![Meus agendamentos](telas/07-meus-agendamentos.png) Meus agendamentos | ![Cancelar](telas/08-cancelar-confirmacao.png) Confirmação de cancelamento |
| ![Remarcar](telas/09-remarcar.png) Remarcar | |

### Celular
| | |
|---|---|
| ![Celular horário](telas/10-celular-agendar-horario.png) | ![Celular meus agendamentos](telas/11-celular-meus-agendamentos.png) |

### Erros
| | |
|---|---|
| ![403](telas/12-erro-403.png) Acesso negado | ![404](telas/13-erro-404.png) Página não encontrada |

### Profissional
| | |
|---|---|
| ![Agenda dia](telas/14-agenda-profissional-dia.png) Agenda do dia | ![Agenda semana](telas/15-agenda-profissional-semana.png) Agenda da semana |

### Administrador
| | |
|---|---|
| ![Painel](telas/16-painel.png) Painel | ![Agendamentos](telas/17-admin-agendamentos.png) Agendamentos |
| ![Serviços](telas/18-admin-servicos.png) Serviços | ![Serviço duplicado](telas/19-admin-servico-duplicado.png) Validação de nome repetido |
| ![Profissionais](telas/20-admin-profissionais.png) Profissionais | ![Profissional](telas/21-admin-profissional-form.png) Edição de profissional |
| ![Jornada](telas/22-admin-jornada.png) Jornada (com erro de sobreposição) | ![Clientes](telas/23-admin-clientes.png) Clientes e faltas |
| ![Configurações](telas/24-admin-configuracoes.png) Configurações | |
