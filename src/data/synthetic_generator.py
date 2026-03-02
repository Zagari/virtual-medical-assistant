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


def generate_all(
    n_patients: int = 80,
    output_dir: Optional[str] = None,
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

    # Resumo
    summary = {
        "pacientes": len(patients_clean),
        "exames": len(all_exams),
        "prontuarios": len(all_consultations),
        "receitas": len(all_prescriptions),
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
        "summary": summary,
    }
