from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.views.generic import TemplateView
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import datetime, timedelta
import os

# SEM IMPORTS DE MODELS (temporário)
# from .models import ... ← REMOVIDO!

def index(request):
    # Dados fake para homepage funcionar
    context = {
        'ultimas_aulas': [],  # lista vazia
        'total_pacientes': 12,
    }
    return render(request, 'index.html', context)

def paciente_list(request):
    # View básica sem models
    pacientes = []  # lista vazia
    return render(request, "core/paciente_list.html", {"pacientes": pacientes})

def paciente_create(request):
    # Form funciona (já corrigido)
    from .forms import PacienteForm
    if request.method == "POST":
        form = PacienteForm(request.POST)
        if form.is_valid():
            messages.success(request, "Paciente salvo!")
            return redirect("core:paciente_list")
    else:
        form = PacienteForm()
    return render(request, "core/paciente_form.html", {"form": form})

def profissional_list(request):
    profissionais = []
    return render(request, "core/profissional_list.html", {"profissionais": profissionais})

def profissional_create(request):
    from .forms import ProfissionalForm
    if request.method == "POST":
        form = ProfissionalForm(request.POST)
        if form.is_valid():
            messages.success(request, "Profissional salvo!")
            return redirect("core:profissional_list")
    else:
        form = ProfissionalForm()
    return render(request, "core/profissional_form.html", {"form": form})

def servico_list(request):
    servicos = []
    return render(request, "core/servico_list.html", {"servicos": servicos})

def servico_create(request):
    from .forms import ServicoForm
    if request.method == "POST":
        form = ServicoForm(request.POST)
        if form.is_valid():
            messages.success(request, "Serviço salvo!")
            return redirect("core:servico_list")
    else:
        form = ServicoForm()
    return render(request, "core/servico_form.html", {"form": form})

def atendimento_list(request):
    atendimentos = []
    return render(request, "core/atendimento_list.html", {"atendimentos": atendimentos})

def atendimento_create(request):
    from .forms import AtendimentoForm
    if request.method == "POST":
        form = AtendimentoForm(request.POST)
        if form.is_valid():
            messages.success(request, "Atendimento agendado!")
            return redirect("core:atendimento_list")
    else:
        form = AtendimentoForm()
    return render(request, "core/atendimento_form.html", {"form": form})

def atendimento_realizado(request, pk):
    messages.info(request, "Funcionalidade em desenvolvimento")
    return redirect("core:atendimento_list")

def comissao_list(request):
    comissoes = []
    return render(request, "core/comissao_list.html", {"comissoes": comissoes})

def agenda_hoje(request):
    hoje = timezone.now().date()
    return redirect("core:agenda_dia", data=hoje.strftime("%Y-%m-%d"))

def agenda_dia(request, data):
    # Agenda fake
    agenda = [
        {"profissional": "João Silva", "horarios": [{"hora": "10:00", "ocupado": False}]},
        {"profissional": "Maria Santos", "horarios": [{"hora": "14:00", "ocupado": True}]}
    ]
    return render(request, "core/agenda_dia.html", {"agenda": agenda, "data": data})

def relatorio_list(request):
    return render(request, "core/relatorio_list.html")

def relatorio_financeiro(request):
    # PDF fake por enquanto
    response = HttpResponse("Relatório em desenvolvimento", content_type='text/plain')
    return response
# 👇 COMENTA Google por enquanto
    # path('google-connect/', views.google_calendar_connect, name='google_connect'),
    # path('google-callback/', views.google_calendar_callback, name='google_callback'),