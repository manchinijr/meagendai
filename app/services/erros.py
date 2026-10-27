"""Exceções de domínio. A mensagem de cada uma é exibida diretamente ao usuário (catálogo E03–E07)."""


class RegraNegocioError(Exception):
    mensagem = "Não foi possível concluir a operação."

    def __init__(self, mensagem=None):
        super().__init__(mensagem or self.mensagem)
        self.mensagem = mensagem or self.mensagem


class HorarioIndisponivelError(RegraNegocioError):
    mensagem = "Esse horário acabou de ser reservado. Escolha outro horário disponível."


class HorarioNoPassadoError(RegraNegocioError):
    mensagem = "Não é possível agendar em um horário que já passou."


class ForaDaJornadaError(RegraNegocioError):
    mensagem = "O profissional não atende nesse horário."


class ServicoNaoRealizadoError(RegraNegocioError):
    mensagem = "Este profissional não realiza o serviço escolhido."


class CancelamentoForaDoPrazoError(RegraNegocioError):
    def __init__(self, horas):
        super().__init__(
            f"Cancelamentos e remarcações são permitidos até {horas} h antes do horário."
        )


class ClienteBloqueadoError(RegraNegocioError):
    mensagem = (
        "Seu agendamento online está bloqueado por faltas. "
        "Entre em contato com o estabelecimento."
    )


class PermissaoNegadaError(RegraNegocioError):
    mensagem = "Você não tem permissão para alterar este agendamento."


class StatusInvalidoError(RegraNegocioError):
    mensagem = "Não é possível alterar o status deste agendamento."


class RegistroDuplicadoError(RegraNegocioError):
    mensagem = "Já existe um registro com esses dados."


class JornadaSobrepostaError(RegraNegocioError):
    mensagem = "Esse período se sobrepõe a outra jornada do mesmo dia."
