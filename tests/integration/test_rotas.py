"""Testes de integração das rotas (Controller + View + banco)."""

from datetime import timedelta

from app import create_app
from app.config import TestConfig
from app.extensions import db
from app.models import Agendamento, Perfil, StatusAgendamento, Usuario
from app.services import agendamento_service

from .conftest import logar


class TestAutenticacao:
    def test_login_invalido_mostra_mensagem(self, client, cliente):
        resposta = logar(client, "cliente@teste.com", "errada123")
        assert "E-mail ou senha incorretos." in resposta.get_data(as_text=True)

    def test_login_redireciona_conforme_o_perfil(self, client, admin):
        resposta = logar(client, "admin@teste.com")
        assert resposta.status_code == 302
        assert resposta.headers["Location"].endswith("/admin")

    def test_cadastro_cria_cliente_e_ja_entra(self, client):
        resposta = client.post("/cadastro", data={
            "nome": "Maria Nova", "email": "Maria@Teste.com", "telefone": "(11) 91234-5678",
            "senha": "Senha123", "confirmar": "Senha123", "aceite": "y",
        })
        assert resposta.status_code == 302
        usuario = db.session.query(Usuario).filter_by(email="maria@teste.com").one()
        assert usuario.perfil == Perfil.CLIENTE
        assert usuario.checar_senha("Senha123")

    def test_cadastro_com_email_repetido_e_recusado(self, client, cliente):
        resposta = client.post("/cadastro", data={
            "nome": "Repetido", "email": "cliente@teste.com", "senha": "Senha123",
            "confirmar": "Senha123", "aceite": "y",
        })
        assert resposta.status_code == 200
        assert "Este e-mail já possui cadastro" in resposta.get_data(as_text=True)

    def test_cadastro_exige_senha_forte_e_aceite(self, client):
        texto = client.post("/cadastro", data={
            "nome": "Fraca", "email": "fraca@teste.com", "senha": "123", "confirmar": "123",
        }).get_data(as_text=True)
        assert "pelo menos 8 caracteres" in texto
        assert "É preciso aceitar os termos" in texto


class TestPermissoes:
    def test_visitante_e_enviado_para_o_login(self, client):
        resposta = client.get("/meus-agendamentos")
        assert resposta.status_code == 302
        assert "/login" in resposta.headers["Location"]

    def test_cliente_nao_acessa_o_admin(self, client, cliente):
        logar(client, "cliente@teste.com")
        assert client.get("/admin").status_code == 403
        assert client.get("/api/painel").status_code == 403

    def test_profissional_nao_acessa_o_agendamento_de_cliente(self, client, barbeiro):
        logar(client, "carlos@teste.com")
        assert client.get("/agendar").status_code == 403

    def test_pagina_inexistente_tem_404_amigavel(self, client):
        resposta = client.get("/nao-existe")
        assert resposta.status_code == 404
        assert "Página não encontrada" in resposta.get_data(as_text=True)


class TestFluxoDoCliente:
    def test_agenda_pelo_formulario(self, client, cliente, barbeiro, corte, as_10h):
        logar(client, "cliente@teste.com")
        resposta = client.post("/agendamentos", data={
            "servico_id": corte.id, "profissional_id": barbeiro.id, "inicio": as_10h.isoformat(),
        }, follow_redirects=True)
        assert "Agendamento confirmado" in resposta.get_data(as_text=True)
        assert db.session.query(Agendamento).count() == 1

    def test_horario_ocupado_mostra_mensagem_e03(self, client, cliente, outro_cliente, barbeiro, corte, as_10h):
        agendamento_service.criar_agendamento(outro_cliente, corte.id, barbeiro.id, as_10h)
        logar(client, "cliente@teste.com")
        resposta = client.post("/agendamentos", data={
            "servico_id": corte.id, "profissional_id": barbeiro.id, "inicio": as_10h.isoformat(),
        }, follow_redirects=True)
        assert "Esse horário acabou de ser reservado" in resposta.get_data(as_text=True)

    def test_cancela_pelo_formulario(self, client, cliente, barbeiro, corte, as_10h):
        ag = agendamento_service.criar_agendamento(cliente, corte.id, barbeiro.id, as_10h)
        logar(client, "cliente@teste.com")
        resposta = client.post(f"/agendamentos/{ag.id}/cancelar", follow_redirects=True)
        assert "Agendamento cancelado." in resposta.get_data(as_text=True)
        db.session.refresh(ag)
        assert ag.status == StatusAgendamento.CANCELADO

    def test_nao_cancela_agendamento_de_outro_cliente(self, client, cliente, outro_cliente, barbeiro, corte, as_10h):
        ag = agendamento_service.criar_agendamento(outro_cliente, corte.id, barbeiro.id, as_10h)
        logar(client, "cliente@teste.com")
        assert client.post(f"/agendamentos/{ag.id}/cancelar").status_code == 403

    def test_api_de_horarios_devolve_json(self, client, cliente, barbeiro, corte, dia_util, as_10h):
        logar(client, "cliente@teste.com")
        dados = client.get(f"/api/horarios?servico={corte.id}&profissional={barbeiro.id}&data={dia_util}").get_json()
        assert dados["data"] == dia_util.isoformat()
        assert {"inicio": as_10h.isoformat(), "rotulo": "10:00"} in dados["horarios"]

    def test_api_de_horarios_valida_parametros(self, client, cliente):
        logar(client, "cliente@teste.com")
        resposta = client.get("/api/horarios")
        assert resposta.status_code == 400
        assert "erro" in resposta.get_json()


class TestAdmin:
    def test_cria_servico(self, client, admin):
        logar(client, "admin@teste.com")
        resposta = client.post("/admin/servicos/novo", data={
            "nome": "Sobrancelha", "duracao_min": 15, "preco": "25.00", "ativo": "y",
        }, follow_redirects=True)
        assert "Serviço salvo." in resposta.get_data(as_text=True)
        assert "Sobrancelha" in client.get("/").get_data(as_text=True)

    def test_servico_com_nome_repetido_e_recusado(self, client, admin, corte):
        logar(client, "admin@teste.com")
        resposta = client.post("/admin/servicos/novo", data={"nome": "Corte", "duracao_min": 30, "preco": "10"})
        assert "Já existe um serviço com esse nome." in resposta.get_data(as_text=True)

    def test_cria_profissional_e_jornada(self, client, admin, corte):
        logar(client, "admin@teste.com")
        resposta = client.post("/admin/profissionais/novo", data={
            "nome": "Ana Lima", "email": "ana@teste.com", "senha": "Senha123", "servicos": [corte.id], "ativo": "y",
        })
        assert resposta.status_code == 302
        usuario = db.session.query(Usuario).filter_by(email="ana@teste.com").one()
        assert usuario.perfil == Perfil.PROFISSIONAL
        prof_id = usuario.profissional.id
        client.post(f"/admin/profissionais/{prof_id}/jornada", data={"dia_semana": 0, "hora_inicio": "09:00", "hora_fim": "12:00"})
        sobreposta = client.post(
            f"/admin/profissionais/{prof_id}/jornada",
            data={"dia_semana": 0, "hora_inicio": "11:00", "hora_fim": "14:00"},
            follow_redirects=True,
        )
        assert "se sobrepõe a outra jornada" in sobreposta.get_data(as_text=True)
        db.session.refresh(usuario.profissional)
        assert len(usuario.profissional.jornadas) == 1

    def test_api_do_painel(self, client, admin, cliente, barbeiro, corte, as_10h):
        agendamento_service.criar_agendamento(cliente, corte.id, barbeiro.id, as_10h)
        logar(client, "admin@teste.com")
        dia = as_10h.date()
        dados = client.get(f"/api/painel?ini={dia}&fim={dia}").get_json()
        assert dados["total"] == 1
        assert dados["faturamento_previsto"] == 45.0

    def test_api_do_painel_recusa_periodo_invertido(self, client, admin):
        logar(client, "admin@teste.com")
        resposta = client.get("/api/painel?ini=2030-02-10&fim=2030-02-01")
        assert resposta.status_code == 400

    def test_configuracoes_alteram_a_regra(self, client, admin):
        logar(client, "admin@teste.com")
        client.post("/admin/configuracoes", data={"ANTECEDENCIA_CANCEL_H": 0, "LIMITE_FALTAS": 5, "PASSO_SLOT_MIN": 30})
        from app.services import config_service
        assert config_service.todas() == {"ANTECEDENCIA_CANCEL_H": 0, "LIMITE_FALTAS": 5, "PASSO_SLOT_MIN": 30}

    def test_zerar_faltas(self, client, admin, cliente):
        logar(client, "admin@teste.com")
        client.post(f"/admin/clientes/{cliente.id}/zerar-faltas")
        db.session.refresh(cliente)
        assert cliente.faltas_zeradas_em is not None


class TestSeguranca:
    def test_formulario_sem_token_csrf_e_recusado(self, app, cliente):
        class ComCsrf(TestConfig):
            WTF_CSRF_ENABLED = True

        app_csrf = create_app(ComCsrf)
        resposta = app_csrf.test_client().post("/login", data={"email": "cliente@teste.com", "senha": "Senha123"})
        assert resposta.status_code == 400

    def test_login_nao_redireciona_para_outro_site(self, client, cliente):
        resposta = client.post("/login?next=https://site-malicioso.com", data={"email": "cliente@teste.com", "senha": "Senha123"})
        assert "site-malicioso" not in resposta.headers["Location"]

    def test_senha_e_guardada_com_hash(self, cliente):
        assert cliente.senha_hash != "Senha123"
        assert len(cliente.senha_hash) > 40


def test_remarcacao_pela_rota(client, cliente, barbeiro, corte, as_10h):
    ag = agendamento_service.criar_agendamento(cliente, corte.id, barbeiro.id, as_10h)
    logar(client, "cliente@teste.com")
    assert client.get(f"/agendamentos/{ag.id}/remarcar").status_code == 200
    novo_inicio = as_10h + timedelta(hours=1)
    resposta = client.post(f"/agendamentos/{ag.id}/remarcar", data={"inicio": novo_inicio.isoformat()}, follow_redirects=True)
    assert "Agendamento remarcado" in resposta.get_data(as_text=True)


class TestProfissional:
    def test_agenda_do_dia_e_da_semana(self, client, cliente, barbeiro, corte, as_10h):
        agendamento_service.criar_agendamento(cliente, corte.id, barbeiro.id, as_10h)
        logar(client, "carlos@teste.com")
        dia = as_10h.date().isoformat()
        assert "Cliente Teste" in client.get(f"/agenda?data={dia}").get_data(as_text=True)
        semana = client.get(f"/agenda?data={dia}&visao=semana").get_data(as_text=True)
        assert "Cliente Teste" in semana
        assert "Sábado" in semana

    def test_marca_falta_pela_rota(self, client, cliente, barbeiro, corte, as_10h):
        ag = agendamento_service.criar_agendamento(cliente, corte.id, barbeiro.id, as_10h)
        ag.inicio = ag.inicio - timedelta(days=30)  # simula um atendimento que já aconteceu
        ag.fim = ag.fim - timedelta(days=30)
        db.session.commit()
        logar(client, "carlos@teste.com")
        resposta = client.post(f"/agenda/{ag.id}/status", data={"status": "FALTOU"}, follow_redirects=True)
        assert "Atendimento marcado como faltou." in resposta.get_data(as_text=True)
        assert agendamento_service.faltas_do_cliente(cliente) == 1

    def test_status_invalido_mostra_erro(self, client, cliente, barbeiro, corte, as_10h):
        ag = agendamento_service.criar_agendamento(cliente, corte.id, barbeiro.id, as_10h)
        logar(client, "carlos@teste.com")
        resposta = client.post(f"/agenda/{ag.id}/status", data={"status": "REALIZADO"}, follow_redirects=True)
        assert "depois do horário de início" in resposta.get_data(as_text=True)
