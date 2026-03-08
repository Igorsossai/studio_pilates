from django.shortcuts import render, redirect
from django.db.models import Sum, Count  # para relatórios
from django.contrib import messages
# ... outros imports ...
from .models import Paciente, Profissional, Servico
from .forms import PacienteForm, ProfissionalForm, ServicoForm

def paciente_list(request):
    pacientes = Paciente.objects.all().order_by("nome")
    return render(request, "core/paciente_list.html", {"pacientes": pacientes})


def paciente_create(request):
    if request.method == "POST":
        form = PacienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("core:paciente_list")
    else:
        form = PacienteForm()
    return render(request, "core/paciente_form.html", {"form": form})
def profissional_list(request):
    profissionais = Profissional.objects.all().order_by("nome_completo")
    return render(request, "core/profissional_list.html", {"profissionais": profissionais})


def profissional_create(request):
    if request.method == "POST":
        form = ProfissionalForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("core:profissional_list")
    else:
        form = ProfissionalForm()
    return render(request, "core/profissional_form.html", {"form": form})
def servico_list(request):
    servicos = Servico.objects.all().order_by("nome")
    return render(request, "core/servico_list.html", {"servicos": servicos})


def servico_create(request):
    if request.method == "POST":
        form = ServicoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("core:servico_list")
    else:
        form = ServicoForm()
    return render(request, "core/servico_form.html", {"form": form})


def atendimento_list(request):
    atendimentos = Atendimento.objects.select_related(
        "paciente", "profissional", "servico"
    ).order_by("-data", "hora_inicio")
    return render(request, "core/atendimento_list.html", {"atendimentos": atendimentos})


def atendimento_create(request):
    if request.method == "POST":
        form = AtendimentoForm(request.POST)
        if form.is_valid():
            atendimento = form.save()
            # Calcula valor baseado no serviço
            atendimento.valor_cobrado = atendimento.servico.preco_padrao
            atendimento.save()
            return redirect("core:atendimento_list")
    else:
        form = AtendimentoForm()

    # Filtra só profissionais ativos
    form.fields["profissional"].queryset = Profissional.objects.filter(ativo=True)

    return render(request, "core/atendimento_form.html", {"form": form})


from django.shortcuts import render, redirect
from .models import Paciente, Profissional, Servico, Atendimento  # confirma imports
from .forms import PacienteForm, ProfissionalForm, ServicoForm, AtendimentoForm  # confirma AtendimentoForm


# Suas views anteriores de paciente/profissional/servico...


# NOVAS VIEWS DE ATENDIMENTO
def atendimento_list(request):
    atendimentos = Atendimento.objects.select_related(
        "paciente", "profissional", "servico"
    ).order_by("-data", "hora_inicio")
    return render(request, "core/atendimento_list.html", {"atendimentos": atendimentos})


def atendimento_create(request):
    if request.method == "POST":
        form = AtendimentoForm(request.POST)
        if form.is_valid():
            atendimento = form.save()
            # Calcula valor baseado no serviço
            atendimento.valor_cobrado = atendimento.servico.preco_padrao
            atendimento.save()
            return redirect("core:atendimento_list")
    else:
        form = AtendimentoForm()

    # Filtra só profissionais ativos
    form.fields["profissional"].queryset = Profissional.objects.filter(ativo=True)

    return render(request, "core/atendimento_form.html", {"form": form})


from django.contrib import messages
from django.shortcuts import get_object_or_404
from .models import Comissao


def atendimento_realizado(request, pk):
    atendimento = get_object_or_404(Atendimento, pk=pk)

    if request.method == "POST":
        if atendimento.status == "AGENDADO":
            atendimento.status = "REALIZADO"
            atendimento.save()

            # CALCULA COMISSÃO AUTOMÁTICA
            comissao, created = Comissao.objects.get_or_create(
                atendimento=atendimento,
                profissional=atendimento.profissional,
                defaults={
                    "valor": atendimento.valor_cobrado * (atendimento.profissional.porcentagem_comissao / 100)
                }
            )
            messages.success(request,
                             f"Atendimento marcado como realizado! Comissão de R$ {comissao.valor:.2f} calculada.")
            return redirect("core:atendimento_list")
        else:
            messages.error(request, "Atendimento já foi processado.")

    return render(request, "core/atendimento_realizado.html", {"atendimento": atendimento})
def comissao_list(request):
    comissoes = Comissao.objects.select_related("atendimento__paciente", "profissional").order_by("-atendimento__data")
    return render(request, "core/comissao_list.html", {"comissoes": comissoes})


from django.utils import timezone
from datetime import datetime, timedelta
from dateutil import parser  # pip install python-dateutil


def agenda_hoje(request):
    hoje = timezone.now().date()
    return redirect("core:agenda_dia", data=hoje.strftime("%Y-%m-%d"))


def agenda_dia(request, data):
    try:
        data_obj = parser.parse(data).date()
    except:
        data_obj = timezone.now().date()

    # Horários padrão (8h-20h, intervalos de 60min)
    hora_inicio = datetime.combine(data_obj, datetime.min.time()).replace(hour=8)
    hora_fim = datetime.combine(data_obj, datetime.min.time()).replace(hour=20)

    profissionais = Profissional.objects.filter(ativo=True)

    # Horários livres/ocupados por profissional
    agenda = []
    for prof in profissionais:
        horarios_livres = []
        atendimentos = Atendimento.objects.filter(
            profissional=prof, data=data_obj
        ).order_by("hora_inicio")

        hora_atual = hora_inicio
        while hora_atual < hora_fim:
            proximo_horario = hora_atual + timedelta(minutes=60)

            # Verifica se tem atendimento nesse horário
            tem_atendimento = atendimentos.filter(
                hora_inicio__gte=hora_atual,
                hora_inicio__lt=proximo_horario
            ).exists()

            horarios_livres.append({
                "hora": hora_atual.strftime("%H:%M"),
                "ocupado": tem_atendimento,
                "atendimento": atendimentos.filter(hora_inicio=hora_atual).first() if tem_atendimento else None
            })

            hora_atual = proximo_horario

        agenda.append({
            "profissional": prof,
            "horarios": horarios_livres
        })

    anterior = (data_obj - timedelta(days=1)).strftime("%Y-%m-%d")
    proximo = (data_obj + timedelta(days=1)).strftime("%Y-%m-%d")

    return render(request, "core/agenda_dia.html", {
        "data": data_obj.strftime("%d/%m/%Y"),
        "anterior": anterior,
        "proximo": proximo,
        "agenda": agenda
    })


from django.http import JsonResponse
from django.shortcuts import redirect
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import pickle
import os
from datetime import datetime

SCOPES = ['https://www.googleapis.com/auth/calendar']


def google_calendar_connect(request):
    profissional_id = request.GET.get('profissional_id')
    profissional = get_object_or_404(Profissional, id=profissional_id)

    flow = InstalledAppFlow.from_client_secrets_file(
        'core/credentials.json', SCOPES)

    flow.redirect_uri = request.build_absolute_uri('/google_calendar_callback/')
    authorization_url, state = flow.authorization_url(
        access_type='offline', include_granted_scopes='true')

    request.session['google_state'] = state
    request.session['profissional_id'] = profissional_id

    return redirect(authorization_url)


def google_calendar_callback(request):
    state = request.session['google_state']
    profissional_id = request.session['profissional_id']
    profissional = get_object_or_404(Profissional, id=profissional_id)

    flow = InstalledAppFlow.from_client_secrets_file(
        'core/credentials.json', SCOPES)

    flow.fetch_token(authorization_response=request.build_absolute_uri())
    credentials = flow.credentials

    token_data = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'token_expiry': credentials.expiry
    }

    GoogleCalendarToken.objects.update_or_create(
        profissional=profissional,
        defaults=token_data
    )

    messages.success(request, f"Google Calendar conectado para {profissional.nome_completo}!")
    return redirect('core:profissional_list')


from django.http import HttpResponse
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from django.db.models import Sum
from datetime import datetime
from dateutil.relativedelta import relativedelta


def relatorio_financeiro(request):
    mes = request.GET.get('mes', datetime.now().strftime('%Y-%m'))
    ano, mes = mes.split('-')

    inicio_mes = datetime(int(ano), int(mes), 1)
    fim_mes = inicio_mes + relativedelta(months=1) - relativedelta(days=1)

    # Dados do mês
    atendimentos_realizados = Atendimento.objects.filter(
        status="REALIZADO", data__range=[inicio_mes.date(), fim_mes.date()]
    )

    total_receita = atendimentos_realizados.aggregate(Sum('valor_cobrado'))['valor_cobrado__sum'] or 0
    total_comissoes = Comissao.objects.filter(
        atendimento__data__range=[inicio_mes.date(), fim_mes.date()]
    ).aggregate(Sum('valor'))['valor__sum'] or 0

    comissoes_prof = Comissao.objects.filter(
        atendimento__data__range=[inicio_mes.date(), fim_mes.date()]
    ).values('profissional__nome_completo').annotate(
        total=Sum('valor'), atendimentos=Count('atendimento')
    ).order_by('-total')

    # Gerar PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="relatorio_{mes}_{ano}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()

    # Título
    title = Paragraph(f"<b>RELATÓRIO FINANCEIRO</b><br/><br/>Mês: {mes}/{ano}", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 20))

    # Resumo
    resumo_data = [
        ['Resumo Mensal', 'Valor'],
        ['Total Receita', f'R$ {total_receita:,.2f}'],
        ['Total Comissões', f'R$ {total_comissoes:,.2f}'],
        ['Lucro Líquido', f'R$ {total_receita - total_comissoes:,.2f}'],
        ['Atendimentos', atendimentos_realizados.count()]
    ]
    resumo_tabela = Table(resumo_data)
    resumo_tabela.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(resumo_tabela)
    story.append(Spacer(1, 20))

    # Comissões por profissional
    comissao_data = [['Profissional', 'Atendimentos', 'Comissão']]
    for c in comissoes_prof:
        comissao_data.append([
            c['profissional__nome_completo'],
            c['atendimentos'],
            f'R$ {c["total"]:,.2f}'
        ])

    comissao_tabela = Table(comissao_data)
    comissao_tabela.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(Paragraph("<b>Comissões por Profissional</b>", styles['Heading2']))
    story.append(comissao_tabela)

    doc.build(story)
    return response

def relatorio_list(request):
    """Página inicial de relatórios com botões"""
    return render(request, "core/relatorio_list.html")
