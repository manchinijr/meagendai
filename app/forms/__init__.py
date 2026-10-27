from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DecimalField,
    EmailField,
    IntegerField,
    PasswordField,
    SelectField,
    SelectMultipleField,
    StringField,
    TextAreaField,
    TimeField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    InputRequired,
    Length,
    NumberRange,
    Optional,
    Regexp,
    ValidationError,
)
from wtforms.widgets import CheckboxInput, ListWidget

from app.models.jornada import DIAS_SEMANA

OBRIGATORIO = "Campo obrigatório."
TELEFONE = Regexp(r"^\(?\d{2}\)?\s?9?\d{4}-?\d{4}$", message="Informe um telefone válido, ex.: (11) 91234-5678.")


class SenhaForte:
    def __call__(self, form, field):
        senha = field.data or ""
        if len(senha) < 8 or not any(c.isdigit() for c in senha) or not any(c.isalpha() for c in senha):
            raise ValidationError("A senha deve ter pelo menos 8 caracteres, com letras e números.")


class LoginForm(FlaskForm):
    email = EmailField("E-mail", validators=[DataRequired(OBRIGATORIO), Email("E-mail inválido.")])
    senha = PasswordField("Senha", validators=[DataRequired(OBRIGATORIO)])
    lembrar = BooleanField("Manter conectado")


class CadastroForm(FlaskForm):
    nome = StringField("Nome completo", validators=[DataRequired(OBRIGATORIO), Length(3, 100)])
    email = EmailField("E-mail", validators=[DataRequired(OBRIGATORIO), Email("E-mail inválido.")])
    telefone = StringField("Telefone (WhatsApp)", validators=[Optional(), TELEFONE])
    senha = PasswordField("Senha", validators=[DataRequired(OBRIGATORIO), SenhaForte()])
    confirmar = PasswordField(
        "Confirme a senha", validators=[DataRequired(OBRIGATORIO), EqualTo("senha", "As senhas não conferem.")]
    )
    aceite = BooleanField(
        "Li e aceito o uso dos meus dados somente para os agendamentos (LGPD).",
        validators=[DataRequired("É preciso aceitar os termos para criar a conta.")],
    )


class ServicoForm(FlaskForm):
    nome = StringField("Nome", validators=[DataRequired(OBRIGATORIO), Length(2, 80)])
    descricao = TextAreaField("Descrição", validators=[Optional(), Length(max=255)])
    duracao_min = IntegerField(
        "Duração (min)", validators=[DataRequired(OBRIGATORIO), NumberRange(5, 480, "Entre 5 e 480 minutos.")]
    )
    preco = DecimalField(
        "Preço (R$)", places=2, validators=[DataRequired(OBRIGATORIO), NumberRange(0, message="Preço inválido.")]
    )
    ativo = BooleanField("Ativo", default=True)


class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


class ProfissionalForm(FlaskForm):
    nome = StringField("Nome", validators=[DataRequired(OBRIGATORIO), Length(3, 100)])
    email = EmailField("E-mail de acesso", validators=[DataRequired(OBRIGATORIO), Email("E-mail inválido.")])
    telefone = StringField("Telefone", validators=[Optional(), TELEFONE])
    especialidade = StringField("Especialidade", validators=[Optional(), Length(max=80)])
    senha = PasswordField("Senha de acesso", validators=[Optional(), SenhaForte()])
    servicos = MultiCheckboxField("Serviços que realiza", coerce=int)
    ativo = BooleanField("Ativo", default=True)


class JornadaForm(FlaskForm):
    dia_semana = SelectField("Dia", coerce=int, choices=list(enumerate(DIAS_SEMANA)))
    hora_inicio = TimeField("Início", validators=[DataRequired(OBRIGATORIO)])
    hora_fim = TimeField("Fim", validators=[DataRequired(OBRIGATORIO)])


class ConfiguracaoForm(FlaskForm):
    ANTECEDENCIA_CANCEL_H = IntegerField(
        "Antecedência mínima para cancelar (horas)", validators=[InputRequired(OBRIGATORIO), NumberRange(0, 168)]
    )
    LIMITE_FALTAS = IntegerField(
        "Faltas que bloqueiam o agendamento online", validators=[InputRequired(OBRIGATORIO), NumberRange(1, 20)]
    )
    PASSO_SLOT_MIN = IntegerField(
        "Intervalo entre horários (min)", validators=[InputRequired(OBRIGATORIO), NumberRange(5, 120)]
    )


class AcaoForm(FlaskForm):
    """Formulário vazio: só carrega o token CSRF em botões de ação (cancelar, marcar status etc.)."""
