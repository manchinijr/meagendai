-- MeAgendaí: projeto físico do banco de dados (PostgreSQL 16+)
-- Execução: flask init-db   (ou psql -f database/schema.sql)

CREATE EXTENSION IF NOT EXISTS btree_gist;

CREATE TABLE usuario (
  id                SERIAL PRIMARY KEY,
  nome              VARCHAR(100) NOT NULL CHECK (length(trim(nome)) >= 3),
  email             VARCHAR(120) NOT NULL UNIQUE,
  telefone          VARCHAR(20),
  senha_hash        VARCHAR(255) NOT NULL,
  perfil            VARCHAR(12)  NOT NULL CHECK (perfil IN ('ADMIN', 'PROFISSIONAL', 'CLIENTE')),
  ativo             BOOLEAN      NOT NULL DEFAULT TRUE,
  faltas_zeradas_em TIMESTAMPTZ,
  criado_em         TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE TABLE profissional (
  id            SERIAL PRIMARY KEY,
  usuario_id    INTEGER NOT NULL UNIQUE REFERENCES usuario (id) ON DELETE RESTRICT,
  especialidade VARCHAR(80),
  ativo         BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE servico (
  id          SERIAL PRIMARY KEY,
  nome        VARCHAR(80)   NOT NULL UNIQUE,
  descricao   VARCHAR(255),
  duracao_min SMALLINT      NOT NULL CHECK (duracao_min BETWEEN 5 AND 480),
  preco       NUMERIC(10,2) NOT NULL CHECK (preco >= 0),
  ativo       BOOLEAN       NOT NULL DEFAULT TRUE
);

CREATE TABLE profissional_servico (
  profissional_id INTEGER NOT NULL REFERENCES profissional (id) ON DELETE CASCADE,
  servico_id      INTEGER NOT NULL REFERENCES servico (id) ON DELETE CASCADE,
  PRIMARY KEY (profissional_id, servico_id)
);

CREATE TABLE jornada (
  id              SERIAL PRIMARY KEY,
  profissional_id INTEGER  NOT NULL REFERENCES profissional (id) ON DELETE CASCADE,
  dia_semana      SMALLINT NOT NULL CHECK (dia_semana BETWEEN 0 AND 6),  -- 0 = segunda-feira
  hora_inicio     TIME     NOT NULL,
  hora_fim        TIME     NOT NULL,
  CHECK (hora_fim > hora_inicio),
  -- dois períodos do mesmo dia não podem se sobrepor
  EXCLUDE USING gist (
    profissional_id WITH =,
    dia_semana WITH =,
    tsrange('2000-01-01'::date + hora_inicio, '2000-01-01'::date + hora_fim) WITH &&
  )
);

CREATE TABLE agendamento (
  id              SERIAL PRIMARY KEY,
  cliente_id      INTEGER       NOT NULL REFERENCES usuario (id) ON DELETE RESTRICT,
  profissional_id INTEGER       NOT NULL REFERENCES profissional (id) ON DELETE RESTRICT,
  servico_id      INTEGER       NOT NULL REFERENCES servico (id) ON DELETE RESTRICT,
  inicio          TIMESTAMPTZ   NOT NULL,
  fim             TIMESTAMPTZ   NOT NULL,
  status          VARCHAR(10)   NOT NULL DEFAULT 'AGENDADO'
                  CHECK (status IN ('AGENDADO', 'CANCELADO', 'REALIZADO', 'FALTOU')),
  preco_cobrado   NUMERIC(10,2) NOT NULL CHECK (preco_cobrado >= 0),
  observacao      VARCHAR(255),
  criado_em       TIMESTAMPTZ   NOT NULL DEFAULT now(),
  atualizado_em   TIMESTAMPTZ   NOT NULL DEFAULT now(),
  CHECK (fim > inicio),
  -- RN01: o mesmo profissional não pode ter dois atendimentos sobrepostos
  EXCLUDE USING gist (profissional_id WITH =, tstzrange(inicio, fim) WITH &&)
    WHERE (status <> 'CANCELADO')
);

CREATE INDEX ix_agendamento_cliente      ON agendamento (cliente_id, inicio);
CREATE INDEX ix_agendamento_profissional ON agendamento (profissional_id, inicio);
CREATE INDEX ix_agendamento_inicio       ON agendamento (inicio);

CREATE TABLE configuracao (
  chave     VARCHAR(40)  PRIMARY KEY,
  valor     VARCHAR(100) NOT NULL,
  descricao VARCHAR(255)
);

INSERT INTO configuracao (chave, valor, descricao) VALUES
  ('ANTECEDENCIA_CANCEL_H', '2',  'Horas mínimas de antecedência para cancelar/remarcar'),
  ('LIMITE_FALTAS',         '3',  'Faltas que bloqueiam novos agendamentos online'),
  ('PASSO_SLOT_MIN',        '15', 'Intervalo, em minutos, entre os horários oferecidos');
