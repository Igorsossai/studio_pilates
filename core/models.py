from django.db import models

class Paciente(models.Model):
    nome = models.CharField(max_length=150)
    data_nascimento = models.DateField(null=True, blank=True)
    cpf = models.CharField(max_length=14, unique=True, null=True, blank=True)
    telefone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    endereco = models.CharField(max_length=255, null=True, blank=True)
    observacoes_gerais = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.nome


class Profissional(models.Model):
    nome_completo = models.CharField(max_length=150)
    registro_conselho = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)  # campo simples
    porcentagem_comissao = models.DecimalField(
        max_digits=5, decimal_places=2, default=40.00, help_text="% por atendimento"
    )
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome_completo

class Servico(models.Model):
    TIPO_CHOICES = (
        ("PILATES", "Pilates"),
        ("FISIO", "Fisioterapia"),
        ("AVALIACAO", "Avaliação"),
        ("OUTRO", "Outro"),
    )
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    duracao_minutos = models.PositiveIntegerField(default=60)
    preco_padrao = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.nome


class Atendimento(models.Model):
    STATUS_CHOICES = (
        ("AGENDADO", "Agendado"),
        ("REALIZADO", "Realizado"),
        ("CANCELADO", "Cancelado"),
        ("FALTA", "Falta"),
    )

    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="atendimentos")
    profissional = models.ForeignKey(Profissional, on_delete=models.CASCADE, related_name="atendimentos")
    servico = models.ForeignKey(Servico, on_delete=models.PROTECT, related_name="atendimentos")
    data = models.DateField()
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="AGENDADO")
    valor_cobrado = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.paciente} - {self.servico} em {self.data} {self.hora_inicio}"

    def sincronizar_google_calendar(self):
        """Cria evento no Google Calendar do profissional"""
        try:
            # Pega token do profissional
            token = self.profissional.googlecalendartoken

            # Reconstrói credenciais
            creds = Credentials(
                token=token.token,
                refresh_token=token.refresh_token,
                token_uri=token.token_uri,
                client_id=token.client_id,
                client_secret=token.client_secret,
                scopes=['https://www.googleapis.com/auth/calendar']
            )

            # Conecta Google Calendar API
            service = build('calendar', 'v3', credentials=creds)

            # Monta evento
            inicio = datetime.combine(self.data, self.hora_inicio).isoformat() + 'Z'
            fim = datetime.combine(self.data, self.hora_fim).isoformat() + 'Z'

            event = {
                'summary': f'{self.paciente.nome} - {self.servico.nome}',
                'start': {'dateTime': inicio, 'timeZone': 'America/Sao_Paulo'},
                'end': {'dateTime': fim, 'timeZone': 'America/Sao_Paulo'},
                'description': f'Valor: R$ {self.valor_cobrado}\nStudio Pilates'
            }

            # Cria evento
            service.events().insert(calendarId='primary', body=event).execute()
            return True

        except Exception as e:
            print(f"Erro sincronizar Google: {e}")
            return False

class Pagamento(models.Model):
    FORMA_CHOICES = (
        ("PIX", "PIX"),
        ("CARTAO", "Cartão"),
        ("DINHEIRO", "Dinheiro"),
        ("OUTRO", "Outro"),
    )

    atendimento = models.ForeignKey(Atendimento, on_delete=models.CASCADE, related_name="pagamentos")
    data_pagamento = models.DateTimeField(auto_now_add=True)
    valor = models.DecimalField(max_digits=8, decimal_places=2)
    forma = models.CharField(max_length=20, choices=FORMA_CHOICES)
    codigo_transacao = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Pagamento {self.valor} - {self.forma}"


class Comissao(models.Model):
    atendimento = models.OneToOneField(Atendimento, on_delete=models.CASCADE, related_name="comissao")
    profissional = models.ForeignKey(Profissional, on_delete=models.CASCADE, related_name="comissoes")
    valor = models.DecimalField(max_digits=8, decimal_places=2)
    pago = models.BooleanField(default=False)
    data_pagamento = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Comissão {self.profissional} - {self.valor}"

    class Prontuario(models.Model):
        atendimento = models.OneToOneField(Atendimento, on_delete=models.CASCADE, related_name="prontuario"
        )

        # Anamnese
        queixa_principal = models.TextField(null=True, blank=True)
        historia_doenca_atual = models.TextField(null=True, blank=True)
        antecedentes_pessoais = models.TextField(null=True, blank=True)
        antecedentes_familiares = models.TextField(null=True, blank=True)
        medicacoes_uso = models.TextField(null=True, blank=True)
        alergias = models.TextField(null=True, blank=True)
        habitos_vida = models.TextField(
            null=True, blank=True, help_text="Ex: sono, alimentação, tabagismo, álcool, atividade física"
        )

        # Exame físico geral
        peso = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
        altura = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
        imc = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
        pressao_arterial = models.CharField(max_length=20, null=True, blank=True)
        frequencia_cardiaca = models.PositiveIntegerField(null=True, blank=True)
        frequencia_respiratoria = models.PositiveIntegerField(null=True, blank=True)

        # Exame físico específico (músculo-esquelético)
        inspecao_postural = models.TextField(null=True, blank=True)
        mobilidade_articular = models.TextField(null=True, blank=True)
        forca_muscular = models.TextField(null=True, blank=True)
        testes_especiais = models.TextField(null=True, blank=True)
        dor_localizacao = models.TextField(null=True, blank=True)
        dor_intensidade = models.CharField(
            max_length=50, null=True, blank=True, help_text="Escala numérica, EVA etc."
        )

        # Evolução / conduta
        descricao_sessao = models.TextField(null=True, blank=True)
        conduta = models.TextField(null=True, blank=True)
        orientacoes_paciente = models.TextField(null=True, blank=True)

        criado_em = models.DateTimeField(auto_now_add=True)
        atualizado_em = models.DateTimeField(auto_now=True)

        def __str__(self):
            return f"Prontuário de {self.atendimento.paciente} - {self.atendimento.data}"

class Prontuario(models.Model):
    atendimento = models.OneToOneField(
        Atendimento, on_delete=models.CASCADE, related_name="prontuario"
    )

    # Anamnese
    queixa_principal = models.TextField(null=True, blank=True)
    historia_doenca_atual = models.TextField(null=True, blank=True)
    antecedentes_pessoais = models.TextField(null=True, blank=True)
    antecedentes_familiares = models.TextField(null=True, blank=True)
    medicacoes_uso = models.TextField(null=True, blank=True)
    alergias = models.TextField(null=True, blank=True)
    habitos_vida = models.TextField(
        null=True, blank=True, help_text="Ex: sono, alimentação, tabagismo, álcool, atividade física"
    )

    # Exame físico geral
    peso = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    altura = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    imc = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    pressao_arterial = models.CharField(max_length=20, null=True, blank=True)
    frequencia_cardiaca = models.PositiveIntegerField(null=True, blank=True)
    frequencia_respiratoria = models.PositiveIntegerField(null=True, blank=True)

    # Exame físico específico (músculo-esquelético)
    inspecao_postural = models.TextField(null=True, blank=True)
    mobilidade_articular = models.TextField(null=True, blank=True)
    forca_muscular = models.TextField(null=True, blank=True)
    testes_especiais = models.TextField(null=True, blank=True)
    dor_localizacao = models.TextField(null=True, blank=True)
    dor_intensidade = models.CharField(
        max_length=50, null=True, blank=True, help_text="Escala numérica, EVA etc."
    )

    # Evolução / conduta
    descricao_sessao = models.TextField(null=True, blank=True)
    conduta = models.TextField(null=True, blank=True)
    orientacoes_paciente = models.TextField(null=True, blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Prontuário de {self.atendimento.paciente} - {self.atendimento.data}"

    class GoogleCalendarToken(models.Model):
        profissional = models.OneToOneField(Profissional, on_delete=models.CASCADE)
        token = models.TextField()
        refresh_token = models.TextField()
        token_expiry = models.DateTimeField()

        def __str__(self):
            return f"Token {self.profissional.nome_completo}"


class GoogleCalendarToken(models.Model):
    profissional = models.OneToOneField(Profissional, on_delete=models.CASCADE)
    token = models.TextField()
    refresh_token = models.TextField()
    token_expiry = models.DateTimeField()

    def __str__(self):
        return f"Token {self.profissional.nome_completo}"
