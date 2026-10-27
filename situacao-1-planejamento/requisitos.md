# Especificação de requisitos

## 1. Requisitos funcionais

| ID | Requisito | Ator | Prioridade | Caso de uso |
|---|---|---|---|---|
| RF01 | Permitir cadastro de cliente (nome, e-mail, telefone, senha e aceite LGPD) e login/logout com perfis ADMIN, PROFISSIONAL e CLIENTE | Todos | Alta | UC01, UC02 |
| RF02 | Manter serviços: nome, descrição, duração, preço e situação (ativo/inativo) | Administrador | Alta | UC11 |
| RF03 | Manter profissionais (com usuário de acesso), vincular os serviços que cada um realiza e cadastrar a jornada semanal | Administrador | Alta | UC12, UC13 |
| RF04 | Consultar horários livres por serviço, profissional e data | Cliente | Alta | UC04 |
| RF05 | Criar agendamento | Cliente | Alta | UC05 |
| RF06 | Cancelar e remarcar agendamento | Cliente, Administrador | Alta | UC06, UC07, UC15 |
| RF07 | Exibir a agenda do profissional (dia e semana) e registrar o atendimento como REALIZADO ou FALTOU | Profissional, Administrador | Alta | UC09, UC10 |
| RF08 | Exibir painel com total de agendamentos, taxa de faltas, faturamento previsto e realizado, agendamentos por dia, serviços mais agendados e próximos atendimentos, com filtro de período e profissional | Administrador | Média | UC14 |
| RF09 | Configurar antecedência mínima para cancelamento, limite de faltas e intervalo entre horários | Administrador | Média | UC17 |
| RF10 | Listar os agendamentos do cliente (próximos e histórico) | Cliente | Alta | UC08 |
| RF11 | Listar clientes com a quantidade de faltas e permitir zerar as faltas | Administrador | Média | UC16 |

## 2. Regras de negócio

| ID | Regra | Onde é garantida |
|---|---|---|
| RN01 | Um profissional não pode ter dois atendimentos com horários sobrepostos (exceto agendamentos cancelados) | `regras.sobrepoe`, `agendamento_service` e constraint `EXCLUDE USING gist` no banco |
| RN02 | Não é permitido agendar no passado, fora da jornada do profissional ou com um profissional que não realiza o serviço | `regras.cabe_na_jornada`, `agendamento_service` |
| RN03 | O cliente só pode cancelar ou remarcar até *N* horas antes do início (padrão: 2 h). O administrador pode cancelar a qualquer momento | `regras.pode_cancelar`, `agendamento_service` |
| RN04 | O cliente com faltas em número igual ou maior que o limite (padrão: 3) fica bloqueado para agendar online até o administrador zerar as faltas | `regras.cliente_bloqueado`, `agendamento_service` |
| RN05 | Os horários são oferecidos em intervalos fixos (padrão: 15 min), e o serviço precisa caber inteiro em um período da jornada | `regras.gerar_horarios_livres` |
| RN06 | Serviços e profissionais inativos não aparecem para agendamento, mas o histórico é preservado (exclusão lógica) | `disponibilidade_service`, `agendamento_service` |
| RN07 | O preço e a duração ficam registrados no agendamento no momento em que ele é criado; alterações posteriores no serviço não mudam o histórico | `agendamento.preco_cobrado` e `agendamento.fim` |
| RN08 | Dois períodos de jornada do mesmo profissional no mesmo dia não podem se sobrepor | `cadastro_service` e constraint `EXCLUDE` na tabela `jornada` |

## 3. Requisitos não funcionais

| ID | Categoria | Requisito | Como foi atendido |
|---|---|---|---|
| RNF01 | Usabilidade | Interface responsiva a partir de 360 px de largura | Bootstrap 5; telas verificadas em 390 px (`ihc/telas/10-*` e `11-*`) |
| RNF02 | Segurança | Senhas armazenadas com hash; proteção CSRF em todos os formulários; consultas parametrizadas; controle de acesso por perfil | Werkzeug (scrypt), Flask-WTF, SQLAlchemy, decorador `perfil_requerido` |
| RNF03 | Desempenho | Respostas em menos de 2 s com o servidor ativo | Índices em `agendamento`; consultas filtradas por dia |
| RNF04 | Usabilidade | Mensagens de erro claras, em português, que digam o que fazer | Catálogo de mensagens em `ihc/README.md` |
| RNF05 | Privacidade (LGPD) | Coletar só os dados necessários e registrar o aceite no cadastro | Campos mínimos e aceite obrigatório |
| RNF06 | Manutenibilidade | Padrão MVC com camada de serviço; cobertura de testes de no mínimo 70% nas regras | Cobertura atual: ~82% geral, ≥ 89% em `services` |
| RNF07 | Acessibilidade | Rótulos em todos os campos, navegação por teclado, link "pular para o conteúdo", contraste adequado | Templates Jinja2 |
| RNF08 | Confiabilidade | Operações compostas (como a remarcação) são atômicas | Transação única em `agendamento_service.remarcar` |
| RNF09 | Portabilidade | Executar em qualquer sistema com Python 3.12+ e PostgreSQL 16 | `requirements.txt`, `docker-compose.yml` |

## 4. Histórias de usuário e critérios de aceite

### HU01: Agendar um serviço (RF04, RF05)
**Como** cliente, **quero** ver só os horários livres do profissional **para** não escolher um horário ocupado.

| # | Dado que | Quando | Então |
|---|---|---|---|
| CA1 | Carlos atende das 9h às 12h e já tem um corte (30 min) às 10h | escolho "Corte" com Carlos nessa data | 09:30 e 10:30 aparecem; 09:45, 10:00 e 10:15 não aparecem |
| CA2 | já passou das 10h05 de hoje | consulto os horários de hoje | o primeiro horário oferecido é 10:15 |
| CA3 | outro cliente reservou o mesmo horário enquanto eu confirmava | clico em "Confirmar" | vejo "Esse horário acabou de ser reservado. Escolha outro horário disponível." |
| CA4 | o profissional não trabalha aos domingos | escolho um domingo | vejo "Nenhum horário livre nesta data. Tente outro dia." |

### HU02: Cancelar um agendamento (RF06)
**Como** cliente, **quero** cancelar meu horário **para** liberá-lo quando não puder comparecer.

| # | Dado que | Quando | Então |
|---|---|---|---|
| CA1 | faltam 3 h para o meu horário e a antecedência mínima é de 2 h | cancelo e confirmo na janela | vejo "Agendamento cancelado." e o horário volta a ficar livre |
| CA2 | falta 1 h para o meu horário | tento cancelar | vejo "Cancelamentos e remarcações são permitidos até 2 h antes do horário." e o agendamento continua ativo |
| CA3 | abri a janela de confirmação | clico em "Manter" | nada é alterado |

### HU03: Remarcar (RF06)
**Como** cliente, **quero** trocar meu horário **sem** perder a vaga atual caso o novo horário não esteja livre.

| # | Dado que | Quando | Então |
|---|---|---|---|
| CA1 | tenho um horário às 10h | remarco para as 14h, que está livre | o horário das 10h é cancelado e o das 14h é criado |
| CA2 | o horário das 11h está ocupado | tento remarcar para as 11h | recebo a mensagem de horário indisponível e meu horário das 10h continua valendo |

### HU04: Registrar falta (RF07, RN04)
**Como** profissional, **quero** marcar quando o cliente falta **para** que o estabelecimento identifique clientes faltosos.

| # | Dado que | Quando | Então |
|---|---|---|---|
| CA1 | o horário do atendimento já começou | clico em "Faltou" | o status muda para FALTOU e a falta conta para o cliente |
| CA2 | o atendimento ainda não começou | tento registrar | vejo "Só é possível registrar o atendimento depois do horário de início." |
| CA3 | o cliente chegou a 3 faltas (limite) | ele tenta agendar | vê o aviso de bloqueio e não consegue escolher serviço |

### HU05: Acompanhar resultados (RF08)
**Como** administrador, **quero** ver indicadores do período **para** acompanhar o faturamento e as faltas.

| # | Dado que | Quando | Então |
|---|---|---|---|
| CA1 | houve 3 atendimentos realizados (R$ 45, R$ 30, R$ 45) e 1 falta no período | abro o painel | vejo faturamento realizado de R$ 120,00 e taxa de faltas de 25% |
| CA2 | não há agendamentos no período | abro o painel | os indicadores mostram zero, sem erro |
| CA3 | informo a data final anterior à inicial | aplico o filtro | vejo "A data final deve ser igual ou posterior à inicial." |

### HU06: Cadastrar jornada (RF03, RN08)
**Como** administrador, **quero** cadastrar os períodos de trabalho de cada profissional, com intervalo de almoço.

| # | Dado que | Quando | Então |
|---|---|---|---|
| CA1 | Carlos trabalha às segundas das 9h às 12h | adiciono 13h–18h na segunda | os dois períodos aparecem e os clientes não veem horários entre 12h e 13h |
| CA2 | já existe 9h–12h na segunda | tento adicionar 11h–14h na segunda | vejo "Esse período se sobrepõe a outra jornada do mesmo dia." |

## 5. Matriz de rastreabilidade (requisito → código → teste)

| Requisito | Código principal | Testes automatizados |
|---|---|---|
| RF01 | `controllers/auth.py`, `services/cadastro_service.py` | `test_rotas.py::TestAutenticacao`, `test_fluxos.py::test_cadastro_valida_no_navegador` |
| RF02 | `controllers/admin.py` (serviços) | `TestAdmin::test_cria_servico`, `test_servico_com_nome_repetido_e_recusado` |
| RF03 / RN08 | `controllers/admin.py` (profissionais, jornada) | `TestAdmin::test_cria_profissional_e_jornada` |
| RF04 / RN05 | `services/disponibilidade_service.py`, `regras.gerar_horarios_livres` | `TestHorariosLivres::*`, `test_rf04_horarios_livres_desconta_agendamentos`, `test_horario_agendado_some_da_lista` |
| RF05 / RN01 | `agendamento_service.criar_agendamento` | `test_rn01_*`, `TestFluxoDoCliente::test_agenda_pelo_formulario`, `test_cliente_agenda_e_cancela` |
| RN02 | `regras.cabe_na_jornada` | `TestCabeNaJornada::*`, `test_rn02_*` |
| RF06 / RN03 | `agendamento_service.cancelar`, `remarcar` | `TestCancelamento::*`, `test_rn03_*`, `test_remarcar_*` |
| RF07 | `controllers/profissional.py`, `agendamento_service.marcar_status` | `test_rf07_*`, `TestProfissional::*` |
| RF08 | `services/relatorio_service.py`, `regras.calcular_metricas` | `TestMetricas::*`, `test_api_do_painel*`, `test_admin_ve_o_painel` |
| RF09 | `services/config_service.py` | `test_configuracoes_alteram_a_regra`, `test_rn04_limite_configuravel` |
| RN04 / RF11 | `agendamento_service.esta_bloqueado`, `zerar_faltas` | `TestBloqueioPorFaltas::*`, `test_rn04_*`, `test_zerar_faltas` |
| RN06 | `disponibilidade_service`, `_validar_novo_horario` | `test_rn06_servico_inativo_nao_pode_ser_agendado` |
| RNF02 | `extensions.py` (CSRF), `models/usuario.py` | `TestSeguranca::*`, `TestPermissoes::*` |
| Front-end (validações) | `static/js/validacoes.js` | `tests/js/validacoes.test.js` |
