# Dicionário de dados

Convenções: **PK** = chave primária · **FK** = chave estrangeira · **UQ** = único · **NN** = não nulo.
Datas e horas com fuso (`TIMESTAMPTZ`) são exibidas no fuso America/Sao_Paulo.

## usuario
Pessoas que acessam o sistema (clientes, profissionais e administradores).

| Coluna | Tipo | Restrições | Domínio / regra | Descrição |
|---|---|---|---|---|
| id | SERIAL | PK | inteiro sequencial | Identificador do usuário |
| nome | VARCHAR(100) | NN | mínimo de 3 caracteres (sem espaços nas pontas) | Nome completo |
| email | VARCHAR(120) | NN, UQ | e-mail válido, gravado em minúsculas | Login do usuário |
| telefone | VARCHAR(20) | | formato (11) 91234-5678 | Contato (WhatsApp) |
| senha_hash | VARCHAR(255) | NN | hash scrypt (nunca a senha pura) | Senha protegida |
| perfil | VARCHAR(12) | NN, CHECK | {ADMIN, PROFISSIONAL, CLIENTE} | Define o que o usuário pode acessar |
| ativo | BOOLEAN | NN, padrão TRUE | | Usuário inativo não consegue entrar |
| faltas_zeradas_em | TIMESTAMPTZ | | | Momento em que o administrador zerou as faltas; só as faltas posteriores contam (RN04) |
| criado_em | TIMESTAMPTZ | NN, padrão now() | | Data do cadastro |

## profissional
Dados profissionais de um usuário com perfil PROFISSIONAL.

| Coluna | Tipo | Restrições | Domínio / regra | Descrição |
|---|---|---|---|---|
| id | SERIAL | PK | | Identificador do profissional |
| usuario_id | INTEGER | NN, UQ, FK → usuario.id (RESTRICT) | relação 1:1 com usuário | Conta de acesso do profissional |
| especialidade | VARCHAR(80) | | texto livre, ex.: "Barbeiro" | Exibida para o cliente |
| ativo | BOOLEAN | NN, padrão TRUE | | Inativo não aparece para agendamento (RN06) |

## servico
Serviços oferecidos pelo estabelecimento.

| Coluna | Tipo | Restrições | Domínio / regra | Descrição |
|---|---|---|---|---|
| id | SERIAL | PK | | Identificador do serviço |
| nome | VARCHAR(80) | NN, UQ | | Nome exibido ao cliente |
| descricao | VARCHAR(255) | | | Detalhes do serviço |
| duracao_min | SMALLINT | NN, CHECK | 5 a 480 minutos | Tempo que o serviço ocupa na agenda |
| preco | NUMERIC(10,2) | NN, CHECK | ≥ 0, em reais | Preço atual |
| ativo | BOOLEAN | NN, padrão TRUE | | Inativo não aparece para agendamento (RN06) |

## profissional_servico
Tabela associativa (N:N) entre profissionais e serviços.

| Coluna | Tipo | Restrições | Descrição |
|---|---|---|---|
| profissional_id | INTEGER | PK, FK → profissional.id (CASCADE) | Profissional |
| servico_id | INTEGER | PK, FK → servico.id (CASCADE) | Serviço que ele realiza |

## jornada
Períodos semanais de trabalho de cada profissional (dois períodos no mesmo dia representam o intervalo de almoço).

| Coluna | Tipo | Restrições | Domínio / regra | Descrição |
|---|---|---|---|---|
| id | SERIAL | PK | | Identificador do período |
| profissional_id | INTEGER | NN, FK → profissional.id (CASCADE) | | Dono da jornada |
| dia_semana | SMALLINT | NN, CHECK | 0 (segunda) a 6 (domingo) | Dia da semana |
| hora_inicio | TIME | NN | | Início do período |
| hora_fim | TIME | NN, CHECK | maior que hora_inicio | Fim do período |
| — | — | EXCLUDE gist | sem sobreposição no mesmo dia e profissional (RN08) | |

## agendamento
Reserva de um serviço por um cliente com um profissional.

| Coluna | Tipo | Restrições | Domínio / regra | Descrição |
|---|---|---|---|---|
| id | SERIAL | PK | | Identificador do agendamento |
| cliente_id | INTEGER | NN, FK → usuario.id (RESTRICT) | usuário com perfil CLIENTE | Quem agendou |
| profissional_id | INTEGER | NN, FK → profissional.id (RESTRICT) | deve realizar o serviço (RN02) | Quem atende |
| servico_id | INTEGER | NN, FK → servico.id (RESTRICT) | serviço ativo na criação (RN06) | Serviço agendado |
| inicio | TIMESTAMPTZ | NN | futuro na criação e dentro da jornada (RN02) | Início do atendimento |
| fim | TIMESTAMPTZ | NN, CHECK | maior que início; = início + duração do serviço no momento | Término do atendimento (RN07) |
| status | VARCHAR(10) | NN, CHECK, padrão AGENDADO | {AGENDADO, CANCELADO, REALIZADO, FALTOU} | Situação (ver diagrama de estados) |
| preco_cobrado | NUMERIC(10,2) | NN, CHECK | ≥ 0; preço do serviço no momento | Valor do atendimento (RN07) |
| observacao | VARCHAR(255) | | | Observação do cliente |
| criado_em | TIMESTAMPTZ | NN, padrão now() | | Data da criação |
| atualizado_em | TIMESTAMPTZ | NN, padrão now() | | Data da última alteração |
| — | — | EXCLUDE gist | mesmo profissional sem horários sobrepostos, exceto CANCELADO (RN01) | |

Índices: `ix_agendamento_cliente (cliente_id, inicio)`, `ix_agendamento_profissional (profissional_id, inicio)`,
`ix_agendamento_inicio (inicio)`.

## configuracao
Parâmetros das regras de negócio, editáveis pelo administrador (RF09).

| Coluna | Tipo | Restrições | Descrição |
|---|---|---|---|
| chave | VARCHAR(40) | PK | Nome do parâmetro |
| valor | VARCHAR(100) | NN | Valor (inteiro armazenado como texto) |
| descricao | VARCHAR(255) | | Explicação do parâmetro |

| Chave | Valor padrão | Faixa aceita | Regra |
|---|---|---|---|
| ANTECEDENCIA_CANCEL_H | 2 | 0 a 168 horas | RN03 |
| LIMITE_FALTAS | 3 | 1 a 20 | RN04 |
| PASSO_SLOT_MIN | 15 | 5 a 120 minutos | RN05 |
