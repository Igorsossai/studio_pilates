from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("pacientes/", views.paciente_list, name="paciente_list"),
    path("pacientes/novo/", views.paciente_create, name="paciente_create"),
    path("profissionais/", views.profissional_list, name="profissional_list"),
    path("profissionais/novo/", views.profissional_create, name="profissional_create"),
    path("servicos/", views.servico_list, name="servico_list"),
    path("servicos/novo/", views.servico_create, name="servico_create"),
    path("atendimentos/", views.atendimento_list, name="atendimento_list"),
    path("atendimentos/novo/", views.atendimento_create, name="atendimento_create"),
    path("atendimentos/<int:pk>/realizado/", views.atendimento_realizado, name="atendimento_realizado"),
    path("comissoes/", views.comissao_list, name="comissao_list"),
    path("agenda/<str:data>/", views.agenda_dia, name="agenda_dia"),
    path("agenda/", views.agenda_hoje, name="agenda_hoje"),
    path("google-connect/", views.google_calendar_connect, name="google_connect"),
    path("google-callback/", views.google_calendar_callback, name="google_callback"),
    path("relatorio/", views.relatorio_financeiro, name="relatorio_financeiro"),
]
