from django.contrib import admin
from .models import (
    Paciente,
    Profissional,
    Servico,
    Atendimento,
    Pagamento,
    Comissao,
    Prontuario,
)

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ("nome", "telefone", "email")
    search_fields = ("nome", "cpf", "email")


@admin.register(Profissional)
class ProfissionalAdmin(admin.ModelAdmin):
    list_display = ("nome_completo", "registro_conselho", "porcentagem_comissao", "ativo")
    search_fields = ("nome_completo", "registro_conselho")


@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ("nome", "tipo", "duracao_minutos", "preco_padrao")
    list_filter = ("tipo",)


@admin.register(Atendimento)
class AtendimentoAdmin(admin.ModelAdmin):
    list_display = ("paciente", "profissional", "servico", "data", "hora_inicio", "status")
    list_filter = ("status", "data", "profissional")
    search_fields = ("paciente__nome",)


@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = ("atendimento", "valor", "forma", "data_pagamento")


@admin.register(Comissao)
class ComissaoAdmin(admin.ModelAdmin):
    list_display = ("profissional", "atendimento", "valor", "pago", "data_pagamento")
    list_filter = ("pago", "profissional")


@admin.register(Prontuario)
class ProntuarioAdmin(admin.ModelAdmin):
    list_display = ("atendimento", "criado_em", "atualizado_em")
    search_fields = ("atendimento__paciente__nome",)