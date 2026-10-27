# MeAgendaí

Sistema web de agendamento online para pequenos prestadores de serviço (barbearias, salões, estúdios e consultórios).
O cliente escolhe o serviço, o profissional e um horário livre; o profissional acompanha a própria agenda; o administrador
cadastra serviços, profissionais e jornadas, e acompanha os resultados em um painel.

Projeto Integrador Transdisciplinar em Engenharia de Software II, Cruzeiro do Sul Virtual.

| | |
|---|---|
| **Aplicação no ar** | _(link do Render, em breve)_ |
| **Vídeo de demonstração** | _(em breve)_ |
| **Vídeo das melhorias pós-testes** | _(em breve)_ |

## Funcionalidades

- **Cliente:** cadastro e login; agendamento em 3 passos (serviço → profissional → horário) com os horários livres
  atualizados sem recarregar a página; "Meus agendamentos" com cancelamento e remarcação.
- **Profissional:** agenda do dia ou da semana; registro de atendimento realizado ou de falta do cliente.
- **Administrador:** painel com indicadores e gráficos; cadastros de serviços, profissionais e jornadas;
  lista de agendamentos; clientes e faltas; configurações das regras.

### Regras de negócio

| Código | Regra |
|---|---|
| RN01 | Um profissional não pode ter dois atendimentos no mesmo horário. A regra é garantida pelo código e também pelo banco (`EXCLUDE USING gist`). |
| RN02 | Não é possível agendar no passado, fora da jornada do profissional ou com um profissional que não realiza o serviço. |
| RN03 | O cliente só pode cancelar ou remarcar até *N* horas antes do horário (padrão: 2 h, configurável). |
| RN04 | O cliente que atinge o limite de faltas (padrão: 3) fica bloqueado para agendar online até o administrador zerar as faltas. |
| RN05 | Os horários são oferecidos a cada 15 min (configurável), e o serviço precisa caber inteiro na jornada. |
| RN06 | Serviços e profissionais inativos deixam de aparecer para agendamento, mas o histórico é preservado. |

## Tecnologias

| Camada | Tecnologia |
|---|---|
| Back-end | Python 3.13, Flask 3 (padrão **MVC** com Blueprints), SQLAlchemy 2, Flask-Login, Flask-WTF |
| Front-end | HTML5, CSS3, JavaScript, Bootstrap 5, Chart.js |
| Banco de dados | PostgreSQL 16 |
| Testes | pytest, pytest-cov, Playwright (E2E) e Vitest (JavaScript) |
| Hospedagem | Render (aplicação) e Neon (PostgreSQL) |
| Integração contínua | GitHub Actions |

## Arquitetura (MVC)

```
Navegador ──HTTP──► Controller (app/controllers) ──► Service (app/services) ──► Model (app/models) ──► PostgreSQL
    ▲                     │
    └──── HTML ◄── View (app/templates)
```

- **Model** (`app/models`): entidades mapeadas com SQLAlchemy.
- **View** (`app/templates`, `app/static`): páginas Jinja2, CSS e JavaScript.
- **Controller** (`app/controllers`): rotas que recebem a requisição, validam o formulário e escolhem a resposta.
- **Service** (`app/services`): regras de negócio isoladas do HTTP, o que permite testá-las sem o navegador.
  As regras puras ficam em `app/services/regras.py`.

## Como executar localmente

Pré-requisitos: Python 3.12+ e Docker (ou um PostgreSQL 16 instalado).

```bash
# 1. Banco de dados local (porta 5433)
docker compose up -d

# 2. Ambiente Python
python -m venv .venv
.venv\Scripts\activate          # Windows  (Linux/macOS: source .venv/bin/activate)
pip install -r requirements-dev.txt

# 3. Configuração
copy .env.example .env          # Linux/macOS: cp .env.example .env

# 4. Tabelas e dados de demonstração
flask init-db
flask seed-demo

# 5. Executar
flask run
```

Acesse http://127.0.0.1:5000.

### Contas de demonstração (criadas pelo `flask seed-demo`)

| Perfil | E-mail | Senha |
|---|---|---|
| Administrador | admin@meagendai.com | Admin@123 |
| Profissional | carlos@meagendai.com | Prof@1234 |
| Profissional | ana@meagendai.com | Prof@1234 |
| Cliente | cliente@meagendai.com | Cliente@123 |

## Testes

```bash
python -m playwright install chromium   # uma única vez, para os testes de navegador
pytest                                  # roda todos os testes
pytest --cov=app                        # com relatório de cobertura
pytest tests/unit                       # só os unitários (não precisam de banco)
npm install && npm test                 # testes do JavaScript (Vitest)
```

| Nível (Modelo V) | Pasta | O que verifica |
|---|---|---|
| Unitário | `tests/unit` | Regras de negócio puras (RN01–RN05) e as métricas do painel |
| Integração | `tests/integration` | Serviços e rotas com PostgreSQL real: permissões, formulários, API, CSRF e a constraint do banco |
| Sistema (E2E) | `tests/e2e` | Fluxos completos no navegador (Playwright): agendar, cancelar, validações do formulário, painel e agenda |

Os nomes dos testes trazem o código da regra que verificam (por exemplo, `test_rn03_bloqueia_cancelamento_em_cima_da_hora`),
o que liga cada requisito ao seu teste.

## Implantação (Render + Neon)

1. No **Neon**, crie o projeto `meagendai` e copie a *connection string* (com `sslmode=require`).
2. No **Render**, crie um *Web Service* a partir deste repositório:
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn "app:create_app()" --workers 2 --bind 0.0.0.0:$PORT`
   - Health check: `/health`
   - Variáveis: `DATABASE_URL` (do Neon), `SECRET_KEY` (aleatória), `FLASK_ENV=production`
3. Com o `DATABASE_URL` do Neon no seu `.env` local, rode uma vez: `flask init-db` e `flask seed-demo`.

> No plano gratuito, o Render "dorme" após 15 minutos sem acesso; o primeiro acesso seguinte pode levar até 1 minuto.

## Documentação

| Situação | Documentos |
|---|---|
| 1. Planejamento | [Escopo](situacao-1-planejamento/escopo-e-visao.md) · [Requisitos](situacao-1-planejamento/requisitos.md) · [UML](situacao-1-planejamento/uml/README.md) · [IHC e telas](situacao-1-planejamento/ihc/README.md) · [Banco de dados](situacao-1-planejamento/banco-de-dados/README.md) · [Dicionário de dados](situacao-1-planejamento/banco-de-dados/dicionario-de-dados.md) · [Kaizen](situacao-1-planejamento/kaizen-feedback.md) |
| 2. Desenvolvimento | [Arquitetura MVC](situacao-2-desenvolvimento/arquitetura-mvc.md) · [Manual de uso](situacao-2-desenvolvimento/manual-de-uso.md) |
| 3. Testes | [Plano de testes](situacao-3-testes/plano-de-testes.md) · [Relatório de testes](situacao-3-testes/relatorio-de-testes.md) · [Formulário dos testadores](situacao-3-testes/formulario-testadores.md) · [Laudo de qualidade](situacao-3-testes/laudo-de-qualidade.md) |

## Estrutura do repositório

```
app/                          código-fonte (MVC)
database/                     script do banco (projeto físico)
tests/                        testes automatizados
situacao-1-planejamento/      documentação de planejamento (requisitos, UML, IHC, banco de dados)
situacao-2-desenvolvimento/   arquitetura e manual de uso
situacao-3-testes/            plano de testes, avaliações dos testadores e laudo de qualidade
```
