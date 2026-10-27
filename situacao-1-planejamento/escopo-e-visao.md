# Escopo e visão do produto

## 1. Problema

Pequenos prestadores de serviço, como barbearias, salões de beleza, estúdios e consultórios, costumam marcar horários por
mensagens de WhatsApp ou ligações. Esse processo:

- toma tempo do profissional, que precisa parar o atendimento para responder mensagens;
- gera **conflitos de horário**, quando dois clientes recebem o mesmo horário;
- não deixa **histórico**, então não se sabe quantos atendimentos foram feitos, quanto foi faturado nem quais clientes faltam com frequência;
- obriga o cliente a esperar uma resposta para saber se há horário livre.

## 2. Proposta

O **MeAgendaí** é um sistema web de agendamento em que o próprio cliente vê apenas os horários realmente livres e
agenda em poucos cliques. O profissional acompanha a sua agenda e o administrador (dono do estabelecimento) cadastra
serviços, profissionais e jornadas e acompanha os resultados em um painel.

## 3. Objetivos

| # | Objetivo | Como será medido |
|---|---|---|
| O1 | Eliminar conflitos de horário | Nenhum agendamento sobreposto para o mesmo profissional (regra garantida também pelo banco de dados) |
| O2 | Permitir que o cliente agende sem intermediários | Agendamento concluído em até 3 passos |
| O3 | Reduzir faltas | Regra de bloqueio após um número configurável de faltas e regra de antecedência mínima para cancelar |
| O4 | Dar visão gerencial ao dono | Painel com total de agendamentos, taxa de faltas e faturamento por período |

## 4. Atores (partes interessadas)

| Ator | Descrição | Principais necessidades |
|---|---|---|
| Visitante | Pessoa que acessa o site sem estar logada | Ver os serviços e criar uma conta |
| Cliente | Pessoa que agenda serviços | Ver horários livres, agendar, cancelar e remarcar |
| Profissional | Quem executa o serviço | Ver a agenda do dia ou da semana; registrar se o atendimento foi realizado ou se o cliente faltou |
| Administrador | Dono ou gerente do estabelecimento | Cadastrar serviços, profissionais e jornadas; acompanhar resultados; definir regras |

## 5. Escopo

### Dentro do escopo (MVP)
- Cadastro e autenticação com três perfis (cliente, profissional e administrador).
- Cadastro de serviços (duração e preço), de profissionais e da jornada semanal de cada um.
- Consulta de horários livres e agendamento em 3 passos.
- Cancelamento e remarcação com antecedência mínima configurável.
- Agenda do profissional (dia e semana) e registro de realizado ou falta.
- Bloqueio de agendamento online por excesso de faltas, com liberação pelo administrador.
- Painel do administrador com indicadores e gráficos.
- Interface responsiva (computador e celular).

### Fora do escopo (possíveis evoluções)
- Pagamento online.
- Notificações por e-mail, SMS ou WhatsApp.
- Vários estabelecimentos (multiempresa) na mesma instalação.
- Aplicativo nativo para celular.
- Folgas e feriados específicos por data (hoje a jornada é semanal).

## 6. Restrições

| Restrição | Origem |
|---|---|
| Back-end em Java, PHP, C#/.NET ou **Python** com padrão **MVC** | Enunciado do Projeto Integrador |
| Front-end em HTML, CSS e JavaScript | Enunciado |
| SGBD popular e de fácil manutenção (**PostgreSQL**) | Enunciado |
| Hospedagem gratuita (Render e Neon) | Orçamento do projeto acadêmico |
| Entrega até o final de novembro de 2026 | Calendário da disciplina |

## 7. Premissas
- O estabelecimento trabalha em um único fuso horário (America/Sao_Paulo).
- Cada atendimento é feito por um único profissional, que atende um cliente por vez.
- O cliente tem acesso a um navegador (computador ou celular).
