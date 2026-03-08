from django.urls import path
from . import views

urlpatterns = [
    # HOME
    path('', views.index, name='index'),

    # PACIENTES
    path('pacientes/', views.paciente_list, name='paciente_list'),
    path('paciente/novo/', views.paciente_create, name='paciente_create'),

    # PROFISSIONAIS
    path('profissionais/', views.profissional_list, name='profissional_list'),
    path('profissional/novo/', views.profissional_create, name='profissional_create'),

    # SERVIÇOS
    path('servicos/', views.servico_list, name='servico_list'),
    path('servico/novo/', views.servico_create, name='servico_create'),

    # ATENDIMENTOS
    path('atendimentos/', views.atendimento_list, name='atendimento_list'),
    path('atendimento/novo/', views.atendimento_create, name='atendimento_create'),

    # AGENDA
    path('agenda/', views.agenda_hoje, name='agenda_hoje'),
    path('agenda/<str:data>/', views.agenda_dia, name='agenda_dia'),

    # RELATÓRIOS
    path('relatorios/', views.relatorio_list, name='relatorio_list'),
    path('relatorio-financeiro/', views.relatorio_financeiro, name='relatorio_financeiro'),

    # COMISSÕES
    path('comissoes/', views.comissao_list, name='comissao_list'),
]
