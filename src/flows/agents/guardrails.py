"""Agente de Guardrails (Segurança) - Valida resposta contra regras de segurança."""

import logging
import re
from datetime import datetime

from src.flows.state import MedicalAssistantState

logger = logging.getLogger(__name__)

# Padrões que indicam prescrição direta
PRESCRIPTION_PATTERNS = [
    r"prescrev[oa]",
    r"tome\s+\d+",
    r"administr[ea]\s+\d+\s*mg",
    r"iniciar?\s+(com\s+)?\d+\s*mg",
    r"receita[r:]",
    r"usar?\s+\d+\s*(mg|ml|comprimido)",
]

# Padrões que indicam diagnóstico definitivo sem ressalvas
DEFINITIVE_DIAGNOSIS_PATTERNS = [
    r"o paciente tem\b",
    r"o diagnóstico é\b",
    r"trata-se de\b",
    r"confirmo que\b",
    r"certamente (é|tem)\b",
]

# Disclaimer obrigatório (variantes aceitas)
DISCLAIMER_KEYWORDS = [
    "validação", "validar", "profissional de saúde",
    "médico responsável", "avaliação clínica",
    "decisão clínica", "confirmar com",
]


def _check_no_prescription(response: str) -> tuple[bool, str | None]:
    """Verifica se a resposta não contém prescrição direta."""
    response_lower = response.lower()
    for pattern in PRESCRIPTION_PATTERNS:
        match = re.search(pattern, response_lower)
        if match:
            return False, (
                f"Prescrição direta detectada: '{match.group()}'. "
                "Reformule como sugestão e indique validação médica."
            )
    return True, None


def _check_human_validation(response: str) -> tuple[bool, str | None]:
    """Verifica se a resposta inclui disclaimer de validação humana."""
    response_lower = response.lower()
    has_disclaimer = any(kw in response_lower for kw in DISCLAIMER_KEYWORDS)
    if not has_disclaimer:
        return False, (
            "Resposta não inclui disclaimer de validação humana. "
            "Adicione uma nota indicando que a resposta deve ser "
            "validada por um profissional de saúde."
        )
    return True, None


def _check_no_definitive_diagnosis(response: str) -> tuple[bool, str | None]:
    """Verifica se a resposta não faz diagnóstico definitivo."""
    response_lower = response.lower()
    for pattern in DEFINITIVE_DIAGNOSIS_PATTERNS:
        match = re.search(pattern, response_lower)
        if match:
            return False, (
                f"Diagnóstico definitivo detectado: '{match.group()}'. "
                "Use linguagem como 'sugere', 'é compatível com', "
                "'deve ser investigado'."
            )
    return True, None


def _check_context_consistency(
    response: str, protocols: list[dict], patient_data: dict | None
) -> tuple[bool, str | None]:
    """Verifica consistência básica da resposta com o contexto."""
    # Se não há contexto, não há o que verificar
    if not protocols and not patient_data:
        return True, None

    # Verificação básica: resposta muito curta pode indicar alucinação
    if len(response.strip()) < 50:
        return False, (
            "Resposta muito curta para o contexto disponível. "
            "Elabore mais utilizando os protocolos e dados fornecidos."
        )

    return True, None


GUARDRAIL_CHECKS = [
    ("no_prescription", _check_no_prescription),
    ("human_validation", _check_human_validation),
    ("no_definitive_diagnosis", _check_no_definitive_diagnosis),
]


def guardrails_agent(state: MedicalAssistantState) -> dict:
    """Valida a resposta do raciocínio contra regras de segurança."""
    draft_response = state.get("draft_response", "")
    retry_count = state.get("retry_count", 0)
    protocols = state.get("protocols", [])
    patient_data = state.get("patient_data")

    logger.info("Guardrails: validando resposta (retry=%d)", retry_count)

    check_results = []
    all_passed = True
    feedback_parts = []

    # Executar checks de regras
    for check_name, check_fn in GUARDRAIL_CHECKS:
        passed, message = check_fn(draft_response)
        check_results.append({
            "rule": check_name,
            "result": "pass" if passed else "fail",
            "message": message,
        })
        if not passed:
            all_passed = False
            feedback_parts.append(message)

    # Check de consistência com contexto
    passed, message = _check_context_consistency(
        draft_response, protocols, patient_data
    )
    check_results.append({
        "rule": "context_consistency",
        "result": "pass" if passed else "fail",
        "message": message,
    })
    if not passed:
        all_passed = False
        feedback_parts.append(message)

    guardrail_result = "aprovado" if all_passed else "reprovado"
    guardrail_feedback = " | ".join(feedback_parts) if feedback_parts else None

    # Incrementar retry_count se reprovado
    new_retry_count = retry_count
    if not all_passed:
        new_retry_count = retry_count + 1
        logger.warning(
            "Guardrails: REPROVADO (retry %d/2) - %s",
            new_retry_count, guardrail_feedback,
        )
    else:
        logger.info("Guardrails: APROVADO")

    # Gerar report amigável para interface
    report_parts = []

    if guardrail_result == "aprovado":
        report_parts.append("**Resultado: ✅ APROVADO**\n")
    else:
        report_parts.append(f"**Resultado: ❌ REPROVADO** (retry {new_retry_count}/2)\n")

    rule_labels = {
        "no_prescription": "Sem prescrição direta",
        "human_validation": "Validação humana mencionada",
        "no_definitive_diagnosis": "Sem diagnóstico definitivo",
        "context_consistency": "Consistência com contexto",
    }

    for check in check_results:
        rule = check["rule"]
        result = check["result"]
        message = check.get("message", "")

        icon = "✅" if result == "pass" else "❌"
        rule_label = rule_labels.get(rule, rule)

        line = f"{icon} **{rule_label}**"
        if result == "fail" and message:
            line += f": {message}"
        report_parts.append(line)

    guardrails_report = "\n".join(report_parts)

    audit_entry = {
        "agent": "guardrails",
        "timestamp": datetime.now().isoformat(),
        "checks": check_results,
        "result": guardrail_result,
        "retry_count": new_retry_count,
    }

    current_reports = state.get("agent_reports", {})
    current_reports["guardrails"] = guardrails_report

    return {
        "guardrail_result": guardrail_result,
        "guardrail_feedback": guardrail_feedback,
        "retry_count": new_retry_count,
        "agent_reports": current_reports,
        "audit_log": state.get("audit_log", []) + [audit_entry],
    }
