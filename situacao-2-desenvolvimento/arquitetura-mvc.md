# Arquitetura do MeAgendaí

## 1. Visão geral

O sistema segue o padrão **MVC (Model–View–Controller)**, recomendado na disciplina, com uma **camada de serviço**
entre o Controller e o Model para concentrar as regras de negócio.

![Arquitetura](../situacao-1-planejamento/uml/08-componentes-mvc.png)

| Camada | Pasta | Responsabilidade | Exemplo |
|---|---|---|---|
| **Model** | `app/models/` | Representa os dados e o mapeamento para as tabelas (SQLAlchemy) | `Agendamento`, `Servico`, `Jornada` |
| **View** | `app/templates/`, `app/static/` | Apresentação: páginas HTML (Jinja2), CSS e JavaScript | `cliente/agendar_horario.html`, `js/agendamento.js` |
| **Controller** | `app/controllers/` | Recebe a requisição HTTP, valida o formulário, chama o serviço e escolhe a View | `cliente.criar_agendamento()` |
| **Service** | `app/services/` | Regras de negócio, sem depender de HTTP | `agendamento_service.criar_agendamento()` |

### Por que uma camada de serviço?
Se as regras ficassem dentro das rotas (controllers), só daria para testá-las simulando requisições HTTP. Separadas em
`services/` e, as puras, em `services/regras.py`, elas são testadas diretamente com `pytest`, inclusive passando um
"agora" fixo para testar horários sem depender do relógio.

## 2. Caminho de uma requisição (exemplo: confirmar agendamento)

1. O navegador envia `POST /agendamentos` com o token CSRF, o serviço, o profissional e o horário.
2. O **Router** do Flask direciona para `controllers/cliente.py::criar_agendamento`.
3. O **Controller** verifica o perfil (`@perfil_requerido(CLIENTE)`) e o token, e converte o horário recebido.
4. O **Service** (`agendamento_service.criar_agendamento`) aplica as regras RN04 (bloqueio), RN06 (ativos),
   RN02 (passado/jornada) e RN01 (sobreposição) e grava o agendamento por meio do **Model**.
5. Se outro cliente gravou o mesmo horário no mesmo instante, o PostgreSQL recusa (constraint `EXCLUDE`) e o
   serviço transforma isso em `HorarioIndisponivelError`.
6. O **Controller** redireciona para "Meus agendamentos" com a mensagem de sucesso, ou volta para a tela de horários
   com a mensagem de erro. A **View** (template) renderiza o HTML.

Diagrama: [`../situacao-1-planejamento/uml/03-sequencia-agendar.png`](../situacao-1-planejamento/uml/03-sequencia-agendar.png).

## 3. Organização do código

```
app/
├── __init__.py            create_app(): configura extensões, registra Blueprints e tratadores de erro
├── config.py              Config (desenvolvimento/produção) e TestConfig
├── extensions.py          db (SQLAlchemy), login_manager, csrf
├── comandos.py            flask init-db | seed-demo | criar-admin
├── filtros.py             filtros de template (data_br, hora, moeda, dia_semana)
├── models/                MODEL
├── services/              SERVICE
│   ├── regras.py              funções puras (RN01–RN05 e métricas)
│   ├── agendamento_service.py criar, cancelar, remarcar, marcar status, faltas
│   ├── disponibilidade_service.py horários livres
│   ├── cadastro_service.py    clientes, serviços, profissionais, jornadas
│   ├── relatorio_service.py   painel
│   ├── config_service.py      parâmetros das regras
│   ├── erros.py               exceções de domínio com a mensagem para o usuário
│   └── tempo.py               fuso horário America/Sao_Paulo
├── controllers/           CONTROLLER (Blueprints)
│   ├── auth.py  cliente.py  profissional.py  admin.py  api.py (JSON)  erros.py (400/403/404/500)
├── forms/                 formulários Flask-WTF (validação no servidor)
├── templates/             VIEW (Jinja2)
└── static/                VIEW (CSS e JavaScript)
```

## 4. Tratamento de erros

| Situação | Tratamento |
|---|---|
| Regra de negócio violada | O serviço lança uma exceção de domínio (`RegraNegocioError` e subclasses); o controller exibe a mensagem com `flash` e devolve o usuário à tela, sem perder o contexto |
| Dados de formulário inválidos | Validação no navegador (JavaScript) e novamente no servidor (Flask-WTF); erros aparecem abaixo de cada campo |
| Corrida entre dois clientes | Constraint `EXCLUDE` no banco; o erro de integridade é convertido em mensagem amigável |
| Acesso indevido | 403 com página amigável (ou JSON na API) |
| Recurso inexistente | 404 com página amigável |
| Token CSRF ausente ou expirado | 400 com "Sua sessão expirou. Recarregue a página e tente novamente." |
| Erro inesperado | 500: rollback da transação, registro no log e página amigável, sem expor detalhes técnicos |
| Falha de rede ao buscar horários | Mensagem na própria tela, sem quebrar a página |

## 5. Segurança

- Senhas com hash (scrypt, via Werkzeug); a senha pura nunca é gravada.
- Proteção CSRF em todos os formulários (Flask-WTF), inclusive no logout.
- Controle de acesso por perfil em cada rota; um cliente só acessa os próprios agendamentos.
- Consultas via ORM (parâmetros), o que evita injeção de SQL.
- Redirecionamento pós-login só para caminhos internos (evita *open redirect*).
- Cookie de sessão `HttpOnly`, `SameSite=Lax` e `Secure` em produção.
- Segredos (`SECRET_KEY`, `DATABASE_URL`) em variáveis de ambiente, fora do repositório.

## 6. Tecnologias e bibliotecas

| Biblioteca | Uso |
|---|---|
| Flask 3 | Framework web (rotas, templates) |
| Flask-SQLAlchemy / SQLAlchemy 2 | ORM (Model) |
| psycopg 3 | Driver do PostgreSQL |
| Flask-Login | Sessão do usuário autenticado |
| Flask-WTF / WTForms | Formulários, validação e CSRF |
| python-dotenv | Leitura do arquivo `.env` |
| gunicorn | Servidor de produção |
| Bootstrap 5, Bootstrap Icons | Layout responsivo e ícones |
| Chart.js | Gráficos do painel |
| pytest, pytest-cov, Playwright, Vitest | Testes |
