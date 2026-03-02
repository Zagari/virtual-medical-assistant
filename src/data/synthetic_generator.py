"""
Gerador de dados sinteticos para o Assistente Medico Virtual.
Gera pacientes ficticios com comorbidades, exames, prontuarios e receitas
clinicamente coerentes, alinhados as 14 Linhas de Cuidado.
"""

import json
import random
import uuid
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

from faker import Faker

fake = Faker("pt_BR")
Faker.seed(42)
random.seed(42)

# ============================================================================
# BASE DE CONHECIMENTO MEDICO
# ============================================================================

# Condicoes com probabilidade de atribuicao, medicamentos tipicos, exames e CIDs
CONDITIONS = {
    "hipertensao": {
        "probability": 0.45,
        "min_age": 35,
        "sex_bias": None,
        "medications": [
            "losartana 50mg 1x/dia",
            "enalapril 10mg 2x/dia",
            "anlodipino 5mg 1x/dia",
            "hidroclorotiazida 25mg 1x/dia",
            "atenolol 50mg 1x/dia",
        ],
        "exams": [
            {
                "tipo": "MAPA 24h",
                "resultados": lambda: {
                    "PA média diurna": f"{random.randint(125, 155)}/{random.randint(78, 95)} mmHg",
                    "PA média noturna": f"{random.randint(110, 140)}/{random.randint(65, 85)} mmHg",
                    "Descenso noturno": f"{random.randint(5, 15)}%",
                },
                "interpretacao": "Padrão compatível com hipertensão arterial sistêmica.",
            },
            {
                "tipo": "Ecocardiograma",
                "resultados": lambda: {
                    "FE": f"{random.randint(50, 68)}%",
                    "Septo IV": f"{random.uniform(9, 14):.1f} mm",
                    "Átrio esquerdo": f"{random.uniform(32, 45):.1f} mm",
                },
                "interpretacao": "Função sistólica preservada. Avaliar hipertrofia ventricular.",
            },
            {
                "tipo": "Creatinina sérica",
                "resultados": lambda: {
                    "Creatinina": f"{random.uniform(0.7, 1.8):.2f} mg/dL",
                    "TFG estimada": f"{random.randint(45, 110)} mL/min/1.73m²",
                },
                "interpretacao": "Função renal a ser monitorada em paciente hipertenso.",
            },
        ],
        "cid": "I10",
        "cid_texto": "Hipertensão essencial (primária)",
    },
    "diabetes_tipo_2": {
        "probability": 0.28,
        "min_age": 30,
        "sex_bias": None,
        "medications": [
            "metformina 850mg 2x/dia",
            "glibenclamida 5mg 1x/dia",
            "sitagliptina 100mg 1x/dia",
            "empagliflozina 25mg 1x/dia",
            "insulina NPH 10UI à noite",
        ],
        "exams": [
            {
                "tipo": "Hemoglobina glicada (HbA1C)",
                "resultados": lambda: {
                    "HbA1C": f"{random.uniform(6.0, 10.5):.1f}%",
                    "Glicemia média estimada": f"{random.randint(120, 250)} mg/dL",
                },
                "interpretacao": "Controle glicêmico a ser avaliado conforme meta individual.",
            },
            {
                "tipo": "Glicemia de jejum",
                "resultados": lambda: {
                    "Glicemia": f"{random.randint(90, 250)} mg/dL",
                },
                "interpretacao": "Valor a ser correlacionado com HbA1C e quadro clínico.",
            },
            {
                "tipo": "Perfil lipídico",
                "resultados": lambda: {
                    "Colesterol total": f"{random.randint(150, 280)} mg/dL",
                    "HDL": f"{random.randint(30, 70)} mg/dL",
                    "LDL": f"{random.randint(70, 190)} mg/dL",
                    "Triglicerídeos": f"{random.randint(80, 350)} mg/dL",
                },
                "interpretacao": "Avaliar risco cardiovascular associado ao diabetes.",
            },
        ],
        "cid": "E11",
        "cid_texto": "Diabetes mellitus tipo 2",
    },
    "asma": {
        "probability": 0.12,
        "min_age": 5,
        "sex_bias": None,
        "medications": [
            "salbutamol spray 100mcg SOS",
            "budesonida 200mcg 2x/dia",
            "formoterol + budesonida 12/400mcg 2x/dia",
            "montelucaste 10mg 1x/dia",
        ],
        "exams": [
            {
                "tipo": "Espirometria",
                "resultados": lambda: {
                    "VEF1": f"{random.randint(55, 95)}% do previsto",
                    "CVF": f"{random.randint(65, 100)}% do previsto",
                    "VEF1/CVF": f"{random.uniform(0.55, 0.85):.2f}",
                    "Resposta ao BD": f"{random.randint(8, 25)}%",
                },
                "interpretacao": "Padrão obstrutivo com resposta ao broncodilatador.",
            },
            {
                "tipo": "Saturação de O2",
                "resultados": lambda: {
                    "SpO2": f"{random.randint(92, 99)}%",
                },
                "interpretacao": "Oximetria de pulso em repouso.",
            },
        ],
        "cid": "J45",
        "cid_texto": "Asma",
    },
    "depressao": {
        "probability": 0.18,
        "min_age": 18,
        "sex_bias": "F",  # mais prevalente em mulheres
        "medications": [
            "sertralina 50mg 1x/dia",
            "fluoxetina 20mg 1x/dia",
            "escitalopram 10mg 1x/dia",
            "venlafaxina 75mg 1x/dia",
            "amitriptilina 25mg à noite",
        ],
        "exams": [
            {
                "tipo": "Avaliação PHQ-9",
                "resultados": lambda: {
                    "Score PHQ-9": str(random.randint(10, 24)),
                    "Classificação": random.choice(
                        ["moderada", "moderadamente grave", "grave"]
                    ),
                },
                "interpretacao": "Sugere episódio depressivo. Acompanhar evolução.",
            },
            {
                "tipo": "TSH (rastreamento)",
                "resultados": lambda: {
                    "TSH": f"{random.uniform(0.5, 5.0):.2f} mUI/L",
                },
                "interpretacao": "Excluir hipotireoidismo como causa de sintomas depressivos.",
            },
        ],
        "cid": "F32",
        "cid_texto": "Episódio depressivo",
    },
    "dpoc": {
        "probability": 0.09,
        "min_age": 45,
        "sex_bias": None,
        "medications": [
            "tiotrópio 18mcg 1x/dia",
            "salbutamol spray 100mcg SOS",
            "formoterol 12mcg 2x/dia",
            "budesonida + formoterol 400/12mcg 2x/dia",
        ],
        "exams": [
            {
                "tipo": "Espirometria",
                "resultados": lambda: {
                    "VEF1": f"{random.randint(30, 70)}% do previsto",
                    "CVF": f"{random.randint(50, 85)}% do previsto",
                    "VEF1/CVF": f"{random.uniform(0.35, 0.65):.2f}",
                    "Resposta ao BD": f"{random.randint(2, 10)}%",
                },
                "interpretacao": "Padrão obstrutivo sem resposta significativa ao BD. Compatível com DPOC.",
            },
            {
                "tipo": "Gasometria arterial",
                "resultados": lambda: {
                    "pH": f"{random.uniform(7.32, 7.45):.2f}",
                    "pO2": f"{random.randint(55, 85)} mmHg",
                    "pCO2": f"{random.randint(35, 55)} mmHg",
                    "HCO3": f"{random.uniform(22, 30):.1f} mEq/L",
                },
                "interpretacao": "Avaliar presença de hipoxemia e retenção de CO2.",
            },
        ],
        "cid": "J44",
        "cid_texto": "Doença pulmonar obstrutiva crônica",
    },
    "obesidade": {
        "probability": 0.22,
        "min_age": 18,
        "sex_bias": None,
        "medications": [
            "orlistate 120mg 3x/dia",
            "liraglutida 3mg 1x/dia SC",
        ],
        "exams": [
            {
                "tipo": "Avaliação antropométrica",
                "resultados": lambda: {
                    "Peso": f"{random.uniform(85, 140):.1f} kg",
                    "Altura": f"{random.uniform(1.55, 1.85):.2f} m",
                    "IMC": f"{random.uniform(30.0, 45.0):.1f} kg/m²",
                    "Circunferência abdominal": f"{random.randint(95, 130)} cm",
                },
                "interpretacao": "Obesidade. Avaliar comorbidades metabólicas associadas.",
            },
        ],
        "cid": "E66",
        "cid_texto": "Obesidade",
    },
    "hipotireoidismo": {
        "probability": 0.11,
        "min_age": 25,
        "sex_bias": "F",
        "medications": [
            "levotiroxina 50mcg 1x/dia em jejum",
            "levotiroxina 75mcg 1x/dia em jejum",
            "levotiroxina 100mcg 1x/dia em jejum",
        ],
        "exams": [
            {
                "tipo": "TSH e T4 livre",
                "resultados": lambda: {
                    "TSH": f"{random.uniform(4.5, 15.0):.2f} mUI/L",
                    "T4 livre": f"{random.uniform(0.4, 1.0):.2f} ng/dL",
                },
                "interpretacao": "TSH elevado com T4L baixo/normal. Compatível com hipotireoidismo.",
            },
        ],
        "cid": "E03",
        "cid_texto": "Hipotireoidismo",
    },
    "insuficiencia_cardiaca": {
        "probability": 0.06,
        "min_age": 50,
        "sex_bias": None,
        "medications": [
            "enalapril 10mg 2x/dia",
            "carvedilol 6.25mg 2x/dia",
            "furosemida 40mg 1x/dia",
            "espironolactona 25mg 1x/dia",
            "digoxina 0.25mg 1x/dia",
        ],
        "exams": [
            {
                "tipo": "Ecocardiograma",
                "resultados": lambda: {
                    "FE": f"{random.randint(25, 45)}%",
                    "VE diástole": f"{random.randint(50, 70)} mm",
                    "Átrio esquerdo": f"{random.randint(38, 55)} mm",
                    "PSAP": f"{random.randint(25, 55)} mmHg",
                },
                "interpretacao": "Disfunção sistólica do VE. FE reduzida.",
            },
            {
                "tipo": "BNP",
                "resultados": lambda: {
                    "BNP": f"{random.randint(200, 2000)} pg/mL",
                },
                "interpretacao": "BNP elevado, compatível com insuficiência cardíaca.",
            },
        ],
        "cid": "I50",
        "cid_texto": "Insuficiência cardíaca",
    },
    "ansiedade": {
        "probability": 0.12,
        "min_age": 18,
        "sex_bias": "F",
        "medications": [
            "escitalopram 10mg 1x/dia",
            "sertralina 50mg 1x/dia",
            "buspirona 10mg 2x/dia",
            "clonazepam 0.5mg à noite (curto prazo)",
        ],
        "exams": [
            {
                "tipo": "Avaliação GAD-7",
                "resultados": lambda: {
                    "Score GAD-7": str(random.randint(10, 20)),
                    "Classificação": random.choice(["moderada", "grave"]),
                },
                "interpretacao": "Sintomas ansiosos significativos. Acompanhar evolução.",
            },
        ],
        "cid": "F41",
        "cid_texto": "Transtorno de ansiedade generalizada",
    },
}

# Alergias comuns para sorteio aleatorio
COMMON_ALLERGIES = [
    "dipirona",
    "penicilina",
    "sulfa",
    "AAS",
    "ibuprofeno",
    "latex",
    "contraste iodado",
    "amoxicilina",
    "cefalexina",
    "diclofenaco",
]

# Observacoes de prontuario por condicao
CONSULTATION_NOTES = {
    "hipertensao": [
        "Paciente em acompanhamento de HAS. PA aferida em consultório: {pa}. "
        "Orientado sobre dieta hipossódica e atividade física regular. "
        "Manter medicação atual e retorno em {meses} meses.",
        "Retorno de rotina. Refere adesão à medicação. PA: {pa}. "
        "Sem queixas cardiovasculares. Solicitados exames de controle.",
        "Paciente com PA elevada hoje: {pa}. Ajuste de dose realizado. "
        "Reforçadas orientações sobre MEV. Retorno em 30 dias para reavaliação.",
    ],
    "diabetes_tipo_2": [
        "Controle de DM2. HbA1C recente: {hba1c}%. Glicemia capilar hoje: {glic} mg/dL. "
        "Orientado sobre dieta e automonitoramento. Manter esquema atual.",
        "Retorno para avaliação de DM2. Paciente refere episódios de hipoglicemia leve. "
        "Ajustada dose de medicação. Solicitados exames de seguimento.",
        "Consulta de rotina DM2. Exame dos pés: sem alterações. Fundo de olho: solicitado. "
        "Creatinina e microalbuminúria: solicitados. Retorno em {meses} meses.",
    ],
    "asma": [
        "Controle de asma. Paciente refere uso de resgate {resgate}x/semana. "
        "Sem despertar noturno. Espirometria solicitada. Manter corticoide inalatório.",
        "Retorno pós-crise. Paciente estável, sem dispneia em repouso. SpO2: {spo2}%. "
        "Orientado sobre uso correto do dispositivo inalatório. Plano de ação revisado.",
    ],
    "depressao": [
        "Acompanhamento de episódio depressivo. PHQ-9 atual: {phq9}. "
        "Paciente refere melhora parcial dos sintomas com medicação. "
        "Manter ISRS e encaminhar para psicoterapia.",
        "Retorno em {meses} meses de tratamento. Sono melhorado, apetite preservado. "
        "Ainda com dificuldade de concentração. Manter esquema e reavaliar em 60 dias.",
    ],
    "dpoc": [
        "Acompanhamento de DPOC. Paciente refere dispneia aos {esforco}. "
        "SpO2 repouso: {spo2}%. Ex-tabagista há {anos_parou} anos. "
        "Vacinação antigripal e pneumocócica em dia. Manter broncodilatador.",
        "Retorno de rotina DPOC. Sem exacerbações recentes. "
        "Espirometria: VEF1 {vef1}% do previsto. Classe GOLD {gold}. "
        "Manter tratamento e reabilitação pulmonar.",
    ],
    "obesidade": [
        "Acompanhamento de obesidade. Peso atual: {peso} kg, IMC: {imc}. "
        "Paciente em acompanhamento nutricional. Meta: perda de 5-10% em 6 meses. "
        "Orientado sobre atividade física 150min/semana.",
    ],
    "hipotireoidismo": [
        "Controle de hipotireoidismo. TSH recente: {tsh} mUI/L. "
        "Paciente em uso regular de levotiroxina. Sem sintomas de hipo ou hipertireoidismo. "
        "Manter dose e controle em {meses} meses.",
    ],
    "insuficiencia_cardiaca": [
        "Acompanhamento de IC. Classe funcional NYHA {nyha}. Peso: {peso} kg. "
        "Sem edema MMII. Sem ortopneia. BNP recente: {bnp} pg/mL. "
        "Manter otimização terapêutica. Dieta hipossódica.",
        "Retorno IC. Paciente refere dispneia aos {esforco}. "
        "ECO recente: FE {fe}%. Ajuste de diurético realizado. "
        "Retorno em 30 dias.",
    ],
    "ansiedade": [
        "Acompanhamento de TAG. GAD-7 atual: {gad7}. "
        "Paciente em uso de ISRS há {meses_trat} meses. "
        "Refere melhora de sintomas somáticos. Manter medicação e psicoterapia.",
    ],
}


# ============================================================================
# FUNCOES DE GERACAO
# ============================================================================


def _generate_cpf_formatted() -> str:
    """Gera CPF formatado usando Faker."""
    return fake.cpf()


def _random_date_in_range(start_date: date, end_date: date) -> date:
    """Gera uma data aleatoria no intervalo."""
    delta = (end_date - start_date).days
    if delta <= 0:
        return start_date
    return start_date + timedelta(days=random.randint(0, delta))


def _assign_conditions(age: int, sex: str) -> list[str]:
    """Atribui condicoes ao paciente baseado em idade, sexo e probabilidades."""
    conditions = []
    for name, info in CONDITIONS.items():
        if age < info["min_age"]:
            continue
        prob = info["probability"]
        # Ajuste por sexo
        if info["sex_bias"] == sex:
            prob *= 1.3
        elif info["sex_bias"] is not None and info["sex_bias"] != sex:
            prob *= 0.7
        # Ajuste por idade (idosos tem mais comorbidades)
        if age >= 65:
            prob *= 1.2
        if random.random() < prob:
            conditions.append(name)
    # Garantir pelo menos 1 condicao
    if not conditions:
        eligible = [
            n for n, i in CONDITIONS.items() if age >= i["min_age"]
        ]
        conditions.append(random.choice(eligible))
    return conditions


def _get_medications_for_conditions(conditions: list[str]) -> list[str]:
    """Seleciona medicamentos coerentes com as condicoes."""
    meds = []
    for cond in conditions:
        cond_meds = CONDITIONS[cond]["medications"]
        # 1-2 medicamentos por condicao
        n = min(random.randint(1, 2), len(cond_meds))
        meds.extend(random.sample(cond_meds, n))
    return meds


def _get_allergies() -> list[str]:
    """Gera lista aleatoria de alergias (0-3)."""
    n = random.choices([0, 1, 2, 3], weights=[0.5, 0.3, 0.15, 0.05])[0]
    if n == 0:
        return []
    return random.sample(COMMON_ALLERGIES, n)


def generate_patients(n: int = 80) -> list[dict]:
    """Gera n pacientes sinteticos com dados coerentes."""
    patients = []
    for _ in range(n):
        sex = random.choices(["F", "M"], weights=[0.55, 0.45])[0]
        # Idade entre 18 e 88 com distribuicao que favorece adultos/idosos
        age = random.choices(
            range(18, 89),
            weights=[1 if a < 30 else 2 if a < 50 else 3 if a < 70 else 2 for a in range(18, 89)],
        )[0]
        birth_date = date.today() - timedelta(days=age * 365 + random.randint(0, 364))

        if sex == "F":
            name = fake.name_female()
        else:
            name = fake.name_male()

        conditions = _assign_conditions(age, sex)
        medications = _get_medications_for_conditions(conditions)

        patient = {
            "id": str(uuid.uuid4()),
            "nome": name,
            "cpf": _generate_cpf_formatted(),
            "data_nascimento": birth_date.isoformat(),
            "sexo": sex,
            "telefone": fake.phone_number(),
            "endereco": fake.address().replace("\n", ", "),
            "comorbidades": [
                CONDITIONS[c]["cid_texto"] for c in conditions
            ],
            "comorbidades_keys": conditions,  # chaves internas para gerar dados coerentes
            "alergias": _get_allergies(),
            "medicamentos_uso": medications,
        }
        patients.append(patient)

    return patients


def generate_exams(patient: dict) -> list[dict]:
    """Gera 2-4 exames por paciente, coerentes com suas condicoes."""
    exams = []
    # Data dos exames: ultimos 18 meses
    end_date = date.today()
    start_date = end_date - timedelta(days=540)

    for cond in patient["comorbidades_keys"]:
        cond_exams = CONDITIONS[cond]["exams"]
        # 1-2 exames por condicao (mas limitar total a ~4)
        n = min(random.randint(1, 2), len(cond_exams))
        selected = random.sample(cond_exams, n)
        for exam_template in selected:
            exam = {
                "id": str(uuid.uuid4()),
                "paciente_id": patient["id"],
                "tipo": exam_template["tipo"],
                "data": _random_date_in_range(start_date, end_date).isoformat(),
                "resultados": exam_template["resultados"](),  # chama lambda
                "interpretacao": exam_template["interpretacao"],
                "status": random.choices(
                    ["realizado", "realizado", "realizado", "pendente"],
                    weights=[0.7, 0.1, 0.1, 0.1],
                )[0],
            }
            exams.append(exam)

    # Limitar a no maximo 4 exames
    if len(exams) > 4:
        exams = random.sample(exams, 4)

    # Garantir pelo menos 2
    while len(exams) < 2:
        cond = random.choice(patient["comorbidades_keys"])
        template = random.choice(CONDITIONS[cond]["exams"])
        exams.append({
            "id": str(uuid.uuid4()),
            "paciente_id": patient["id"],
            "tipo": template["tipo"],
            "data": _random_date_in_range(start_date, end_date).isoformat(),
            "resultados": template["resultados"](),
            "interpretacao": template["interpretacao"],
            "status": "realizado",
        })

    return exams


def _fill_consultation_template(template: str, cond: str) -> str:
    """Preenche template de consulta com valores aleatorios."""
    replacements = {
        "{pa}": f"{random.randint(125, 170)}/{random.randint(75, 100)} mmHg",
        "{meses}": str(random.choice([3, 4, 6])),
        "{hba1c}": f"{random.uniform(6.5, 10.0):.1f}",
        "{glic}": str(random.randint(95, 250)),
        "{resgate}": str(random.randint(0, 4)),
        "{spo2}": str(random.randint(93, 99)),
        "{phq9}": str(random.randint(8, 22)),
        "{esforco}": random.choice(
            ["pequenos esforços", "médios esforços", "grandes esforços"]
        ),
        "{anos_parou}": str(random.randint(1, 15)),
        "{vef1}": str(random.randint(30, 70)),
        "{gold}": random.choice(["I", "II", "III"]),
        "{peso}": f"{random.uniform(60, 130):.1f}",
        "{imc}": f"{random.uniform(30, 42):.1f}",
        "{tsh}": f"{random.uniform(0.5, 8.0):.2f}",
        "{nyha}": random.choice(["I", "II", "III"]),
        "{bnp}": str(random.randint(150, 1800)),
        "{fe}": str(random.randint(25, 50)),
        "{gad7}": str(random.randint(8, 18)),
        "{meses_trat}": str(random.randint(2, 12)),
    }
    result = template
    for key, val in replacements.items():
        result = result.replace(key, val)
    return result


def generate_consultations(patient: dict) -> list[dict]:
    """Gera 2-5 prontuarios (consultas) por paciente."""
    consultations = []
    end_date = date.today()
    start_date = end_date - timedelta(days=730)  # ultimos 2 anos
    n_consultations = random.randint(2, 5)

    # Gera datas ordenadas
    dates = sorted(
        [_random_date_in_range(start_date, end_date) for _ in range(n_consultations)]
    )

    for i, cons_date in enumerate(dates):
        # Escolhe condicao para esta consulta
        cond = random.choice(patient["comorbidades_keys"])
        cond_info = CONDITIONS[cond]

        # Seleciona template de observacao
        if cond in CONSULTATION_NOTES:
            template = random.choice(CONSULTATION_NOTES[cond])
            obs = _fill_consultation_template(template, cond)
        else:
            obs = f"Consulta de rotina para acompanhamento de {cond_info['cid_texto']}."

        consultation = {
            "id": str(uuid.uuid4()),
            "paciente_id": patient["id"],
            "data": cons_date.isoformat(),
            "diagnostico_cid": cond_info["cid"],
            "diagnostico_texto": cond_info["cid_texto"],
            "observacoes": obs,
        }
        consultations.append(consultation)

    return consultations


def generate_prescriptions(patient: dict) -> list[dict]:
    """Gera 1-3 receitas medicas por paciente."""
    prescriptions = []
    end_date = date.today()
    start_date = end_date - timedelta(days=365)
    n = random.randint(1, 3)

    dates = sorted(
        [_random_date_in_range(start_date, end_date) for _ in range(n)]
    )

    for presc_date in dates:
        cond = random.choice(patient["comorbidades_keys"])
        cond_meds = CONDITIONS[cond]["medications"]
        selected_meds = random.sample(cond_meds, min(random.randint(1, 3), len(cond_meds)))

        prescription = {
            "id": str(uuid.uuid4()),
            "paciente_id": patient["id"],
            "data": presc_date.isoformat(),
            "condicao": CONDITIONS[cond]["cid_texto"],
            "medicamentos": selected_meds,
            "validade_dias": random.choice([30, 60, 90]),
            "observacoes": random.choice([
                "Uso contínuo. Retorno em 3 meses.",
                "Manter medicação e dieta orientada.",
                "Ajuste de dose realizado nesta consulta.",
                "Receita renovada. Sem alterações.",
                "Novo medicamento adicionado ao esquema.",
            ]),
        }
        prescriptions.append(prescription)

    return prescriptions


# ============================================================================
# PROTOCOLOS DE EMERGENCIA SINTETICOS
# ============================================================================

EMERGENCY_PROTOCOLS = {
    "iam": {
        "titulo": "Infarto Agudo do Miocárdio (IAM)",
        "cid": "I21",
        "conteudo": """# Protocolo de Emergência: Infarto Agudo do Miocárdio (IAM)

## Considerações Iniciais

O Infarto Agudo do Miocárdio (IAM) é uma emergência cardiovascular que requer reconhecimento e tratamento imediatos. O tempo é crítico: "tempo é músculo". O objetivo é restaurar o fluxo coronariano o mais rápido possível.

**Definição:** Necrose miocárdica causada por isquemia prolongada, geralmente por oclusão trombótica de artéria coronária sobre placa aterosclerótica instável.

## Reconhecimento e Diagnóstico

### Quadro Clínico Típico
- Dor torácica em aperto/opressão, retroesternal
- Irradiação para membro superior esquerdo, mandíbula, epigástrio
- Duração > 20 minutos, não alivia com repouso ou nitrato
- Sintomas associados: dispneia, sudorese fria, náuseas, palidez

### Apresentações Atípicas (atenção especial)
- Idosos: confusão mental, dispneia isolada
- Diabéticos: IAM silencioso
- Mulheres: fadiga, dispneia, dor epigástrica

### Exames Diagnósticos
1. **ECG em até 10 minutos da chegada**
   - IAMCSST: supradesnível de ST ≥1mm em 2 derivações contíguas
   - IAMSSST: infradesnivelamento de ST, inversão de T, ou ECG normal
2. **Marcadores de necrose miocárdica**
   - Troponina I ou T (alta sensibilidade): colher na admissão e 3-6h
   - CK-MB: menos sensível, útil para reinfarto
3. **Radiografia de tórax:** avaliar congestão pulmonar

## Manejo Inicial (Primeiros 10 minutos)

### MONABCH (mnemônico)
- **M**orfina: 2-4mg IV se dor refratária (cuidado com hipotensão)
- **O**xigênio: apenas se SpO2 < 90%
- **N**itrato: nitroglicerina SL 0,4mg (contraindicado se PAS < 90mmHg ou uso de sildenafil)
- **A**AS: 200-300mg VO mastigado (dose de ataque)
- **B**etabloqueador: metoprolol 5mg IV se FC > 60 e PAS > 100
- **C**lopidogrel: 300-600mg VO (dose de ataque)
- **H**eparina: enoxaparina 1mg/kg SC ou HNF conforme protocolo

### Estratégia de Reperfusão (IAMCSST)
- **Angioplastia primária (preferencial):** se disponível em < 120 minutos
- **Trombólise:** se angioplastia não disponível em tempo hábil
  - Tenecteplase (TNK) dose ajustada por peso
  - Tempo porta-agulha < 30 minutos
  - Contraindicações absolutas: AVC hemorrágico prévio, sangramento ativo

## Monitoramento

### Nas primeiras 24-48 horas
- Monitorização cardíaca contínua (risco de arritmias)
- PA e FC a cada 15-30 minutos inicialmente
- Balanço hídrico rigoroso
- Troponina seriada (pico em 12-24h)
- ECG seriado

### Complicações a monitorar
- Arritmias (FV, TV, BAV)
- Insuficiência cardíaca aguda
- Choque cardiogênico
- Complicações mecânicas (ruptura de parede livre, CIV, insuficiência mitral aguda)

## Indicadores de Qualidade

| Indicador | Meta |
|-----------|------|
| Tempo porta-ECG | < 10 minutos |
| Tempo porta-balão (angioplastia) | < 90 minutos |
| Tempo porta-agulha (trombólise) | < 30 minutos |
| AAS nas primeiras 24h | > 95% |
| Betabloqueador na alta | > 85% |
| Estatina na alta | > 95% |

## Critérios de Alta da Emergência

- Estabilidade hemodinâmica por > 24h
- Sem arritmias malignas
- Revascularização realizada ou programada
- Orientação sobre medicamentos e sinais de alarme
- Encaminhamento para reabilitação cardíaca

---
*Protocolo complementar sintético para fins educacionais. Não substitui protocolos institucionais validados.*
""",
    },
    "avc": {
        "titulo": "Acidente Vascular Cerebral (AVC)",
        "cid": "I64",
        "conteudo": """# Protocolo de Emergência: Acidente Vascular Cerebral (AVC)

## Considerações Iniciais

O AVC é uma emergência neurológica onde "tempo é cérebro". A cada minuto de isquemia cerebral, aproximadamente 1,9 milhão de neurônios são perdidos. O reconhecimento precoce e tratamento em janela terapêutica são fundamentais.

**Tipos principais:**
- AVC Isquêmico (85%): oclusão arterial por trombo/êmbolo
- AVC Hemorrágico (15%): ruptura vascular (hemorragia intraparenquimatosa ou subaracnoidea)

## Reconhecimento e Diagnóstico

### Escala de Cincinnati (pré-hospitalar)
- **F**ace: assimetria facial (pedir para sorrir)
- **A**rms: queda de um braço (pedir para elevar ambos)
- **S**peech: fala arrastada ou incompreensível
- **T**ime: hora do início dos sintomas (fundamental!)

### Sintomas de Alerta
- Déficit motor ou sensitivo súbito (face, braço, perna)
- Alteração de fala ou linguagem
- Alteração visual (perda de campo, diplopia)
- Cefaleia súbita intensa ("a pior da vida" - subaracnoidea)
- Alteração de equilíbrio ou coordenação
- Rebaixamento de consciência

### Exames Diagnósticos Imediatos
1. **TC de crânio sem contraste (em até 25 min)**
   - Exclui hemorragia
   - Pode ser normal nas primeiras horas do AVC isquêmico
2. **Glicemia capilar** (hipoglicemia pode mimetizar AVC)
3. **ECG** (FA é causa comum de AVC cardioembólico)
4. **Laboratório:** hemograma, coagulograma, função renal, eletrólitos

### Escala NIHSS
- Quantifica gravidade do déficit neurológico (0-42 pontos)
- Deve ser aplicada por profissional treinado
- Guia decisão terapêutica e prognóstico

## Manejo Inicial

### Medidas Gerais
- Cabeceira a 0° (ou 30° se risco de aspiração ou PIC elevada)
- Oxigênio apenas se SpO2 < 94%
- Acesso venoso calibroso
- Monitorização cardíaca e PA
- Jejum até avaliação de deglutição

### Controle Pressórico
- **Candidato a trombólise:** PA < 185/110 mmHg antes e < 180/105 após
- **Não candidato:** só tratar se PA > 220/120 mmHg (redução gradual, máx 15%)
- **AVC hemorrágico:** manter PAS entre 140-180 mmHg

### Trombólise Intravenosa (AVC Isquêmico)
**Critérios de inclusão:**
- Déficit neurológico mensurável
- TC sem hemorragia
- Tempo < 4,5 horas do início dos sintomas

**Dose:** Alteplase (rtPA) 0,9 mg/kg (máx 90mg)
- 10% em bolus, restante em 60 minutos

**Contraindicações absolutas:**
- Hemorragia intracraniana na TC
- AVC ou TCE grave nos últimos 3 meses
- Sangramento ativo
- Plaquetas < 100.000
- Uso de anticoagulantes com INR > 1,7

### Trombectomia Mecânica
- Oclusão de grande vaso (carótida interna, ACM proximal)
- Janela estendida até 24h em casos selecionados (DAWN/DEFUSE 3)
- Encaminhar para centro com neurointervenção

## Monitoramento

### Nas primeiras 24 horas
- NIHSS seriado (a cada 1h nas primeiras 6h pós-trombólise)
- PA a cada 15 minutos nas primeiras 2h pós-rtPA
- Vigiar sinais de sangramento
- Glicemia a cada 6h (evitar hipo e hiperglicemia)
- TC de controle em 24h ou se piora neurológica

### Complicações
- Transformação hemorrágica
- Edema cerebral maligno
- Crises convulsivas
- Pneumonia aspirativa
- TVP/TEP

## Indicadores de Qualidade

| Indicador | Meta |
|-----------|------|
| Tempo porta-TC | < 25 minutos |
| Tempo porta-agulha | < 60 minutos |
| Trombólise em elegíveis | > 80% |
| Disfagia avaliada antes de dieta | 100% |
| Profilaxia de TVP em 48h | > 95% |
| Alta com antitrombótico | > 95% |

## Prevenção Secundária

- Antiagregação (AAS ou clopidogrel) ou anticoagulação (se FA)
- Estatina de alta potência
- Controle de PA (meta < 130/80 mmHg)
- Controle glicêmico
- Cessação do tabagismo
- Investigação etiológica completa

---
*Protocolo complementar sintético para fins educacionais. Não substitui protocolos institucionais validados.*
""",
    },
    "sepse": {
        "titulo": "Sepse e Choque Séptico",
        "cid": "A41",
        "conteudo": """# Protocolo de Emergência: Sepse e Choque Séptico

## Considerações Iniciais

Sepse é uma disfunção orgânica potencialmente fatal causada por resposta desregulada do hospedeiro à infecção. O reconhecimento precoce e tratamento nas primeiras horas ("golden hour") reduzem significativamente a mortalidade.

**Definições (Sepsis-3, 2016):**
- **Sepse:** infecção + disfunção orgânica (SOFA ≥ 2 pontos)
- **Choque séptico:** sepse + necessidade de vasopressor para PAM ≥ 65 mmHg + lactato > 2 mmol/L após ressuscitação volêmica adequada

## Reconhecimento e Diagnóstico

### Triagem - qSOFA (quick SOFA)
Dois ou mais critérios sugerem sepse:
- Frequência respiratória ≥ 22 irpm
- Alteração do nível de consciência (Glasgow < 15)
- Pressão arterial sistólica ≤ 100 mmHg

### Critérios de Disfunção Orgânica (SOFA)
- **Respiratório:** PaO2/FiO2 < 400
- **Cardiovascular:** PAM < 70 ou necessidade de vasopressor
- **Neurológico:** Glasgow < 15
- **Renal:** creatinina > 1,2 ou débito urinário < 0,5 mL/kg/h
- **Hepático:** bilirrubina > 1,2 mg/dL
- **Hematológico:** plaquetas < 150.000

### Focos Infecciosos Comuns
- Pulmonar (pneumonia) - mais comum
- Urinário (pielonefrite, ITU complicada)
- Abdominal (peritonite, colangite, abscessos)
- Pele e partes moles (celulite, fasciite)
- Cateter venoso central
- Sistema nervoso central (meningite)

### Exames Diagnósticos
1. **Hemoculturas (2 pares)** - antes do antibiótico, se possível
2. **Lactato arterial** - marcador de hipoperfusão
3. **Hemograma, função renal e hepática, coagulograma**
4. **Gasometria arterial**
5. **Culturas específicas** conforme suspeita (urocultura, LCR, etc.)
6. **Imagem** conforme foco suspeito

## Pacote da Primeira Hora (Hour-1 Bundle)

### 1. Medir Lactato
- Repetir se lactato inicial > 2 mmol/L

### 2. Hemoculturas Antes do Antibiótico
- 2 pares de sítios diferentes
- Não atrasar antibiótico se coleta demorar > 45 min

### 3. Antibiótico de Amplo Espectro
**Iniciar em até 1 hora do reconhecimento**

Esquemas empíricos sugeridos:
- **Foco pulmonar comunitário:** ceftriaxona + azitromicina
- **Foco pulmonar hospitalar:** piperacilina-tazobactam ou meropenem
- **Foco abdominal:** piperacilina-tazobactam ou meropenem + metronidazol
- **Foco urinário:** ceftriaxona ou ciprofloxacino
- **Sem foco definido:** piperacilina-tazobactam ou meropenem

Considerar vancomicina se: MRSA, cateter, infecção de pele

### 4. Ressuscitação Volêmica
- Cristaloide 30 mL/kg nas primeiras 3 horas se hipotensão ou lactato ≥ 4
- Ringer lactato ou SF 0,9%
- Reavaliar responsividade a volume (elevação passiva de MMII, variação de PP)

### 5. Vasopressores se Hipotensão Persistente
- **Noradrenalina** (1ª escolha): iniciar 0,1 mcg/kg/min
- Meta: PAM ≥ 65 mmHg
- Acesso venoso central preferencial (pode iniciar em periférico)
- Considerar **vasopressina** como segundo agente

## Monitoramento

### Metas nas Primeiras 6 Horas
- PAM ≥ 65 mmHg
- Débito urinário ≥ 0,5 mL/kg/h
- Lactato em queda (clearance > 10%/2h)
- SvcO2 ≥ 70% (se disponível)
- Melhora da perfusão periférica (tempo de enchimento capilar)

### Reavaliação Contínua
- Resposta ao volume (evitar hiper-hidratação)
- Necessidade de vasopressor
- Adequação do antibiótico (resultados de cultura)
- Controle de foco (drenagem de abscessos, remoção de cateter)

## Medidas Adicionais

### Controle de Foco
- Drenagem de coleções/abscessos
- Remoção de dispositivos infectados
- Desbridamento cirúrgico se necessário
- Realizar em até 6-12 horas se possível

### Corticosteroides
- **Indicação:** choque séptico refratário a volume e vasopressor
- **Dose:** hidrocortisona 200 mg/dia (50 mg 6/6h ou infusão contínua)

### Hemotransfusão
- Transfundir se Hb < 7 g/dL (meta 7-9 g/dL)
- Exceto: isquemia miocárdica, sangramento ativo

## Indicadores de Qualidade

| Indicador | Meta |
|-----------|------|
| Lactato coletado em 1h | > 95% |
| Hemocultura antes do ATB | > 90% |
| Antibiótico em 1h | > 95% |
| Ressuscitação 30 mL/kg em 3h | > 90% |
| Reavaliação de lactato | > 90% |
| Mortalidade hospitalar | Monitorar tendência |

---
*Protocolo complementar sintético para fins educacionais. Baseado em Surviving Sepsis Campaign 2021.*
""",
    },
    "pneumonia": {
        "titulo": "Pneumonia Adquirida na Comunidade (PAC)",
        "cid": "J18",
        "conteudo": """# Protocolo de Emergência: Pneumonia Adquirida na Comunidade (PAC)

## Considerações Iniciais

A Pneumonia Adquirida na Comunidade (PAC) é uma infecção aguda do parênquima pulmonar adquirida fora do ambiente hospitalar. É causa importante de morbidade e mortalidade, especialmente em idosos e pacientes com comorbidades.

**Agentes etiológicos mais comuns:**
- *Streptococcus pneumoniae* (pneumococo) - principal
- *Mycoplasma pneumoniae* e *Chlamydophila pneumoniae* (atípicos)
- *Haemophilus influenzae*
- Vírus respiratórios (Influenza, SARS-CoV-2, VSR)
- *Legionella pneumophila* (casos graves)

## Diagnóstico

### Quadro Clínico
- Febre (pode estar ausente em idosos)
- Tosse (seca ou produtiva)
- Dispneia
- Dor torácica pleurítica
- Crepitações ou sopro tubário à ausculta
- Taquipneia, taquicardia
- Confusão mental (especialmente em idosos)

### Exames Diagnósticos
1. **Radiografia de tórax**
   - Confirma diagnóstico: infiltrado/consolidação
   - Avalia extensão e complicações (derrame pleural)
2. **Saturação de O2 / Gasometria**
   - SpO2 < 92% indica gravidade
3. **Laboratório**
   - Hemograma, PCR, função renal, eletrólitos
   - Ureia > 65 mg/dL = fator de gravidade
4. **Culturas (casos graves ou internados)**
   - Hemocultura (2 amostras)
   - Cultura de escarro (se disponível e adequado)
   - Antígeno urinário para pneumococo e Legionella

### Diagnósticos Diferenciais
- Tuberculose pulmonar
- Embolia pulmonar
- Edema pulmonar
- Neoplasia pulmonar
- Pneumonite química/aspirativa

## Estratificação de Gravidade

### Escore CURB-65
| Critério | Pontos |
|----------|--------|
| **C**onfusão mental | 1 |
| **U**reia > 50 mg/dL (ou > 7 mmol/L) | 1 |
| **R**espiratória (FR ≥ 30) | 1 |
| **B**lood pressure (PAS < 90 ou PAD ≤ 60) | 1 |
| Idade ≥ **65** anos | 1 |

**Interpretação:**
- 0-1 ponto: tratamento ambulatorial
- 2 pontos: considerar internação (enfermaria)
- 3-5 pontos: PAC grave, considerar UTI

### Critérios de Internação em UTI (ATS/IDSA)
**Critérios maiores (1 = UTI):**
- Choque séptico com necessidade de vasopressor
- Insuficiência respiratória com necessidade de VMI

**Critérios menores (≥ 3 = considerar UTI):**
- FR ≥ 30 irpm
- PaO2/FiO2 ≤ 250
- Infiltrado multilobar
- Confusão/desorientação
- Ureia ≥ 65 mg/dL
- Leucopenia (< 4.000)
- Plaquetopenia (< 100.000)
- Hipotermia (< 36°C)
- Hipotensão requerendo volume agressivo

## Tratamento

### Paciente Ambulatorial (CURB-65 0-1, sem comorbidades)
- **Amoxicilina** 500 mg 8/8h por 5-7 dias, OU
- **Azitromicina** 500 mg 1x/dia por 3-5 dias, OU
- **Claritromicina** 500 mg 12/12h por 7 dias

### Paciente Ambulatorial com Comorbidades
- **Amoxicilina-clavulanato** 875/125 mg 12/12h + macrolídeo, OU
- **Quinolona respiratória** (levofloxacino 750 mg ou moxifloxacino 400 mg) 1x/dia por 5-7 dias

### Paciente Internado em Enfermaria
- **Ceftriaxona** 1-2g IV 1x/dia + **Azitromicina** 500 mg IV/VO 1x/dia, OU
- **Ampicilina-sulbactam** 1,5-3g IV 6/6h + macrolídeo, OU
- **Quinolona respiratória** IV/VO monoterapia

### Paciente em UTI
- **Ceftriaxona** 2g IV 1x/dia + **Azitromicina** 500 mg IV 1x/dia, OU
- **Ceftriaxona** + **Quinolona respiratória**
- Se suspeita de *Pseudomonas*: **Piperacilina-tazobactam** ou **Cefepime** + quinolona/aminoglicosídeo

### Duração do Tratamento
- PAC leve/moderada: 5-7 dias
- PAC grave ou por *Legionella/Pseudomonas*: 7-14 dias
- Critérios de estabilidade para transição IV→VO e alta

## Suporte Clínico

### Oxigenoterapia
- Manter SpO2 92-96% (88-92% se DPOC com retenção crônica de CO2)
- Cateter nasal, máscara, VNI ou IOT conforme necessidade

### Hidratação
- Reposição volêmica se desidratado
- Evitar hiper-hidratação

### Antipiréticos/Analgésicos
- Dipirona ou paracetamol se febre alta ou desconforto

### Profilaxia de TEV
- Enoxaparina 40 mg SC 1x/dia em pacientes internados

## Monitoramento e Reavaliação

### Critérios de Melhora Clínica (48-72h)
- Temperatura < 37,8°C
- FC < 100 bpm
- FR < 24 irpm
- PAS ≥ 90 mmHg
- SpO2 ≥ 90% em ar ambiente
- Tolerância à via oral
- Estado mental basal

### Falha Terapêutica
Se não houver melhora em 48-72h:
- Reavaliar diagnóstico (TB, TEP, neoplasia)
- Avaliar complicações (empiema, abscesso)
- Considerar resistência ou patógeno não coberto
- Ampliar espectro antimicrobiano

## Indicadores de Qualidade

| Indicador | Meta |
|-----------|------|
| Radiografia em até 4h da admissão | > 95% |
| Antibiótico em até 4h | > 95% |
| Avaliação de gravidade documentada | 100% |
| Hemoculturas antes de ATB (graves) | > 90% |
| Transição IV→VO quando estável | > 80% |
| Orientação sobre vacinação na alta | > 90% |

## Prevenção

- **Vacinação antipneumocócica:** VPC13 e PPSV23 para grupos de risco
- **Vacinação anti-influenza:** anual para grupos de risco
- **Cessação do tabagismo**
- **Higiene de mãos**

---
*Protocolo complementar sintético para fins educacionais. Baseado em diretrizes SBPT e IDSA/ATS.*
""",
    },
    "itu": {
        "titulo": "Infecção do Trato Urinário (ITU)",
        "cid": "N39",
        "conteudo": """# Protocolo de Emergência: Infecção do Trato Urinário (ITU)

## Considerações Iniciais

A Infecção do Trato Urinário (ITU) é uma das infecções bacterianas mais comuns na prática clínica. Abrange desde cistite não complicada até pielonefrite e urosepse, com abordagens terapêuticas distintas.

**Classificação:**
- **ITU baixa (cistite):** infecção limitada à bexiga
- **ITU alta (pielonefrite):** infecção do parênquima renal
- **ITU não complicada:** mulher não gestante, sem alterações anatômicas/funcionais
- **ITU complicada:** homens, gestantes, alterações urológicas, cateter, imunossupressão

**Agentes etiológicos:**
- *Escherichia coli* (70-95% dos casos)
- *Klebsiella pneumoniae*
- *Proteus mirabilis*
- *Enterococcus faecalis*
- *Staphylococcus saprophyticus* (mulheres jovens)

## Diagnóstico

### Cistite - Quadro Clínico
- Disúria (dor/ardência ao urinar)
- Polaciúria (aumento da frequência)
- Urgência miccional
- Dor suprapúbica
- Urina turva ou com odor fétido
- Hematúria (pode ocorrer)
- **Ausência de febre** (diferencia de pielonefrite)

### Pielonefrite - Quadro Clínico
- Febre (> 38°C), calafrios
- Dor lombar (punho-percussão +)
- Náuseas/vômitos
- Sintomas de cistite podem estar presentes
- Pode haver sepse associada

### Exames Diagnósticos

**Cistite não complicada:**
- Pode ser diagnóstico clínico (mulher com sintomas típicos)
- EAS (elementos anormais e sedimento): leucocitúria, bacteriúria, nitrito +
- Urocultura: não obrigatória em cistite não complicada

**Pielonefrite e ITU complicada:**
- EAS + Urocultura com antibiograma (obrigatório)
- Hemograma, PCR, função renal
- Hemoculturas (2 amostras) se febre alta ou sepse
- Exame de imagem (TC ou US) se: não melhora em 48-72h, suspeita de abscesso/obstrução, ITU de repetição

### Critérios Diagnósticos Laboratoriais
- **Bacteriúria significativa:** ≥ 10⁵ UFC/mL (jato médio)
- **Em cateter:** ≥ 10³ UFC/mL
- **Leucocitúria:** > 10 leucócitos/campo ou > 10.000/mL

## Tratamento

### Cistite Não Complicada (Mulheres)
| Antibiótico | Dose | Duração |
|-------------|------|---------|
| Fosfomicina | 3g VO dose única | 1 dia |
| Nitrofurantoína | 100 mg 6/6h | 5 dias |
| Sulfametoxazol-Trimetoprim | 800/160 mg 12/12h | 3 dias |

**Evitar quinolonas** para cistite não complicada (reservar para casos mais graves).

### Cistite em Gestantes
- **Nitrofurantoína** 100 mg 6/6h por 7 dias (evitar no 3º trimestre)
- **Cefalexina** 500 mg 6/6h por 7 dias
- **Amoxicilina-clavulanato** 500/125 mg 8/8h por 7 dias
- Urocultura de controle obrigatória após tratamento

### Cistite Complicada / ITU em Homens
- Urocultura obrigatória
- **Quinolona** (ciprofloxacino 500 mg 12/12h) por 7 dias, OU
- **SMX-TMP** 800/160 mg 12/12h por 7 dias
- Investigar causas: HPB, estenose, cálculos

### Pielonefrite Não Complicada (Tratamento Ambulatorial)
Critérios para tratamento ambulatorial: paciente estável, tolera VO, sem vômitos

- **Ciprofloxacino** 500 mg 12/12h por 7 dias, OU
- **Levofloxacino** 750 mg 1x/dia por 5 dias, OU
- **Ceftriaxona** 1g IM dose única seguido de cefalosporina VO

### Pielonefrite com Internação
Indicações: sepse, vômitos, gestante, obstrução, não melhora ambulatorial

- **Ceftriaxona** 1-2g IV 1x/dia, OU
- **Ciprofloxacino** 400 mg IV 12/12h, OU
- **Piperacilina-tazobactam** 4,5g IV 6/6h (se risco de resistência)
- **Gentamicina** pode ser associada em casos graves

Transição para VO quando: afebril > 24h, melhora clínica, tolerância oral.
Duração total: 10-14 dias.

### ITU Associada a Cateter (ITU-AC)
- Trocar cateter antes de iniciar antibiótico (se possível)
- Coletar urocultura do novo cateter
- Tratar por 7 dias (14 dias se resposta lenta)
- Remover cateter assim que possível

## Manejo de Complicações

### Abscesso Renal / Perinefrético
- Drenagem percutânea ou cirúrgica
- Antibioticoterapia prolongada (2-4 semanas)

### Obstrução Urinária com Infecção
- **Emergência urológica**: desobstrução urgente
- Cateter duplo J ou nefrostomia
- Antibiótico de amplo espectro

### Urosepse
- Seguir protocolo de sepse (Hour-1 Bundle)
- Ressuscitação volêmica
- Antibiótico de amplo espectro
- Avaliação urológica para desobstrução se necessário

## Situações Especiais

### Bacteriúria Assintomática
**Tratar apenas em:**
- Gestantes (risco de pielonefrite e parto prematuro)
- Antes de procedimentos urológicos invasivos

**NÃO tratar em:**
- Idosos
- Diabéticos
- Pacientes com cateter de demora
- Mulheres na pós-menopausa

### ITU de Repetição (≥ 2 em 6 meses ou ≥ 3 em 1 ano)
- Investigar causas (imagem, avaliação urológica)
- Profilaxia: nitrofurantoína 100 mg/noite ou pós-coito
- Medidas comportamentais: hidratação, urinar pós-coito, cranberry (?)

## Monitoramento

### Seguimento
- Cistite não complicada: controle clínico (urocultura se sintomas persistem)
- Pielonefrite: urocultura de controle 48-72h se não melhora
- Gestantes: urocultura mensal após tratamento

### Critérios de Melhora (Pielonefrite)
- Defervescência em 48-72h
- Melhora da dor lombar
- Estabilidade hemodinâmica
- Normalização de leucocitose

## Indicadores de Qualidade

| Indicador | Meta |
|-----------|------|
| Urocultura antes de ATB (pielonefrite) | > 95% |
| ATB adequado conforme cultura | > 90% |
| Evitar quinolona em cistite simples | > 80% |
| Investigação de ITU complicada | 100% |
| Tratamento de bacteriúria em gestantes | 100% |

---
*Protocolo complementar sintético para fins educacionais. Baseado em diretrizes SBI e IDSA.*
""",
    },
}


def generate_emergency_protocols(output_dir: Optional[str] = None) -> list[dict]:
    """Gera protocolos de emergencia sinteticos em formato Markdown."""
    if output_dir is None:
        output_dir = str(
            Path(__file__).parent.parent.parent
            / "data"
            / "synthetic"
            / "protocolos_complementares"
        )
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    protocols_generated = []
    print(f"Gerando {len(EMERGENCY_PROTOCOLS)} protocolos de emergência sintéticos...")

    for key, protocol in EMERGENCY_PROTOCOLS.items():
        filename = f"{key}.md"
        filepath = output_path / filename

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(protocol["conteudo"])

        protocols_generated.append({
            "key": key,
            "titulo": protocol["titulo"],
            "cid": protocol["cid"],
            "arquivo": str(filepath),
        })
        print(f"  Salvo: {filename} - {protocol['titulo']}")

    # Salvar indice dos protocolos
    index_path = output_path / "index.json"
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(protocols_generated, f, ensure_ascii=False, indent=2)
    print(f"  Salvo: index.json (índice dos protocolos)")

    return protocols_generated


# ============================================================================
# FUNCAO PRINCIPAL DE GERACAO
# ============================================================================


def generate_all(
    n_patients: int = 80,
    output_dir: Optional[str] = None,
    generate_protocols: bool = True,
) -> dict:
    """Gera todos os dados sinteticos e salva em JSON."""
    if output_dir is None:
        output_dir = str(
            Path(__file__).parent.parent.parent / "data" / "synthetic"
        )
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"Gerando {n_patients} pacientes sintéticos...")
    patients = generate_patients(n_patients)

    all_exams = []
    all_consultations = []
    all_prescriptions = []

    for i, patient in enumerate(patients):
        exams = generate_exams(patient)
        consultations = generate_consultations(patient)
        prescriptions = generate_prescriptions(patient)

        all_exams.extend(exams)
        all_consultations.extend(consultations)
        all_prescriptions.extend(prescriptions)

        if (i + 1) % 20 == 0:
            print(f"  {i + 1}/{n_patients} pacientes processados...")

    # Remover chave interna antes de salvar
    patients_clean = []
    for p in patients:
        p_copy = {k: v for k, v in p.items() if k != "comorbidades_keys"}
        patients_clean.append(p_copy)

    # Salvar arquivos
    files = {
        "pacientes.json": patients_clean,
        "exames.json": all_exams,
        "prontuarios.json": all_consultations,
        "receitas.json": all_prescriptions,
    }

    for filename, data in files.items():
        filepath = output_path / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"  Salvo: {filepath.name} ({len(data)} registros)")

    # Gerar protocolos de emergencia sinteticos
    protocols_generated = []
    if generate_protocols:
        protocols_output_dir = str(output_path / "protocolos_complementares")
        protocols_generated = generate_emergency_protocols(protocols_output_dir)

    # Resumo
    summary = {
        "pacientes": len(patients_clean),
        "exames": len(all_exams),
        "prontuarios": len(all_consultations),
        "receitas": len(all_prescriptions),
        "protocolos_emergencia": len(protocols_generated),
    }
    print(f"\nResumo: {summary}")

    # Estatisticas de condicoes
    condition_counts = {}
    for p in patients:
        for c in p["comorbidades_keys"]:
            condition_counts[c] = condition_counts.get(c, 0) + 1

    print("\nDistribuição de condições:")
    for cond, count in sorted(condition_counts.items(), key=lambda x: -x[1]):
        pct = count / len(patients) * 100
        print(f"  {CONDITIONS[cond]['cid_texto']:<40} {count:>3} ({pct:.0f}%)")

    return {
        "patients": patients,
        "exams": all_exams,
        "consultations": all_consultations,
        "prescriptions": all_prescriptions,
        "protocols": protocols_generated,
        "summary": summary,
    }
