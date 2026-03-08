from django import forms
from .models import Paciente, Profissional, Servico, Atendimento


class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = [
            "nome",
            "data_nascimento",
            "cpf",
            "telefone",
            "email",
            "endereco",
            "observacoes_gerais",
        ]


class ProfissionalForm(forms.ModelForm):
    class Meta:
        model = Profissional
        fields = [
            "nome_completo",
            "registro_conselho",
            "email",
            "porcentagem_comissao",
            "ativo",
        ]



class ServicoForm(forms.ModelForm):
    class Meta:
        model = Servico
        fields = [
            "nome",
            "tipo",
            "duracao_minutos",
            "preco_padrao",
        ]
class AtendimentoForm(forms.ModelForm):
    class Meta:
        model = Atendimento
        fields = [
            "paciente",
            "profissional",
            "servico",
            "data",
            "hora_inicio",
            "hora_fim",
        ]
        widgets = {
            "data": forms.DateInput(attrs={"type": "date"}),
            "hora_inicio": forms.TimeInput(attrs={"type": "time"}),
            "hora_fim": forms.TimeInput(attrs={"type": "time"}),
        }

