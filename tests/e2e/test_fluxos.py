"""Testes de sistema (E2E): fluxos completos no navegador, como um usuário faria."""

import re
from datetime import timedelta

from playwright.sync_api import expect

from app.services.tempo import agora


def proximo_dia_util(dias=2):
    dia = agora().date() + timedelta(days=dias)
    while dia.weekday() >= 5:
        dia += timedelta(days=1)
    return dia


def test_cliente_agenda_e_cancela(page, servidor, entrar):
    entrar("cliente@meagendai.com", "Cliente@123")

    page.click("text=Agendar")
    page.click("text=Corte masculino")
    page.click("text=Carlos Souza")
    expect(page.locator("h1")).to_have_text("Escolha a data e o horário")

    dia = proximo_dia_util()
    page.fill("#data", dia.isoformat())
    page.dispatch_event("#data", "change")
    primeiro = page.locator("#horarios .slot").first
    expect(primeiro).to_have_text("09:00")
    primeiro.click()
    expect(page.locator("#resumo")).to_contain_text("às 09:00")
    page.click("#form-confirmar button[type=submit]")

    expect(page.locator(".alert-success")).to_contain_text("Agendamento confirmado")
    expect(page.locator("main")).to_contain_text("Corte masculino com Carlos Souza")

    page.click("button:has-text('Cancelar')")
    page.click("#modal-cancelar button[type=submit]")
    expect(page.locator(".alert-success")).to_contain_text("Agendamento cancelado.")
    expect(page.locator("main")).to_contain_text("Você não tem agendamentos futuros.")


def test_horario_agendado_some_da_lista(page, servidor, entrar):
    entrar("cliente@meagendai.com", "Cliente@123")
    dia = proximo_dia_util(dias=3)
    page.goto(f"{servidor}/agendar/1/1?data={dia.isoformat()}")
    page.locator("#horarios .slot", has_text="10:00").click()
    page.click("#form-confirmar button[type=submit]")
    expect(page.locator(".alert-success")).to_contain_text("às 10:00")

    page.goto(f"{servidor}/agendar/1/1?data={dia.isoformat()}")
    # Corte dura 30 min: 09:45 terminaria às 10:15 e colidiria com o horário reservado (RN01)
    for livre in ("09:30", "10:30"):
        expect(page.locator("#horarios .slot", has_text=livre)).to_have_count(1)
    for ocupado in ("09:45", "10:00", "10:15"):
        expect(page.locator("#horarios .slot", has_text=ocupado)).to_have_count(0)


def test_cadastro_valida_no_navegador(page, servidor):
    page.goto(f"{servidor}/cadastro")
    page.fill("#telefone", "11912345678")
    expect(page.locator("#telefone")).to_have_value("(11) 91234-5678")

    page.click("form button[type=submit]")
    expect(page.locator("#nome.is-invalid")).to_have_count(1)
    expect(page).to_have_url(f"{servidor}/cadastro")


def test_admin_ve_o_painel(page, servidor, entrar):
    entrar("admin@meagendai.com", "Admin@123")
    expect(page.locator("h1")).to_have_text("Painel")
    expect(page.locator("#m-total")).to_have_text(re.compile(r"^\d+$"))
    expect(page.locator("#m-faturamento_realizado")).to_contain_text("R$")
    expect(page.locator("#grafico-dias")).to_be_visible()


def test_profissional_ve_a_agenda(page, servidor, entrar):
    entrar("carlos@meagendai.com", "Prof@1234")
    expect(page.locator("h1")).to_have_text("Minha agenda")
    page.click("text=Semana")
    expect(page.locator("main")).to_contain_text("Sábado")
