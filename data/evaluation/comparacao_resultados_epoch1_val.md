# Comparação: Modelo Base vs Fine-Tuned

**Data:** 2026-03-08 22:49

## Métricas Agregadas

### Sobreposição entre modelos (FT vs Baseline)

| Métrica | Valor |
|---------|-------|
| Comprimento médio (Base) | 1048 chars |
| Comprimento médio (Fine-tuned) | 912 chars |
| Ratio de comprimento (FT/Base) | 0.93x |
| BLEU Score | 0.0441 |
| ROUGE-1 F1 | 0.3149 |
| ROUGE-2 F1 | 0.1031 |
| ROUGE-L F1 | 0.1883 |

### Qualidade vs Referência (Ground Truth)

| Métrica | Baseline | Fine-Tuned |
|---------|----------|------------|
| BLEU | 0.0388 | 0.2002 |
| ROUGE-1 F1 | 0.3182 | 0.4224 |
| ROUGE-2 F1 | 0.0877 | 0.2611 |
| ROUGE-L F1 | 0.1748 | 0.3367 |
| Similaridade Semântica | 0.9036 | 0.9234 |

## Comparação por Categoria

### Validacao

**Pergunta 1:** Quais são os sintomas da Sindactilia tipo 3?

<details>
<summary>Ver respostas</summary>

**Resposta do Modelo Base:**
```
A Sindactilia tipo 3 é uma condição genética rara que causa anormalidades na formação dos dedos e das mãos. Os sintomas desta variante incluem:

1. Fusão completa de dedos adjacentes, em uma ou mais mãos, formando dedos conhecidos como "síndactiles compostos".
2. A ausência de algumas falanges, ou seja, os ossos que formam os dedos, resultando em dedos curtos ou malformados.
3. A falta de formação completa dos dedos, incluindo a falta de falanges e falanges parciais.
4. As falanges podem ser cur...
```

**Resposta do Modelo Fine-Tuned:**
```
Quais são os sinais e sintomas da Sindactilia tipo 3? A Ontologia do Fenótipo Humano fornece a seguinte lista de sinais e sintomas para Sindactilia tipo 3. Se a informação estiver disponível, a tabela abaixo inclui a frequência com que o sintoma é observado em pessoas com esta condição. Você pode usar o Dicionário Médico MedlinePlus para procurar as definições desses termos médicos. Sinais e sintomas Número aproximado de pacientes (quando disponível) Anormalidade do tórax 90% Aplasia / hipoplasi...
```

</details>

**Pergunta 2:** Quais são os tratamentos para Queilite glandular?

<details>
<summary>Ver respostas</summary>

**Resposta do Modelo Base:**
```
O tratamento para Queilite glandular, uma condição que envolve a inflamação dos glândulas sebáceas do queixo, pode variar de acordo com o grau de severidade do caso. Geralmente, o tratamento consiste em:

1. Limpeza do local: O queixo deve ser limpo com um produto de higiene adequado diariamente.
2. Medicamentos: Pode ser necessário usar cremes ou gelos com corticosteroides para reduzir a inflamação e aliviar o desconforto. Antibióticos também podem ser prescritos caso a queilite seja causada po...
```

**Resposta do Modelo Fine-Tuned:**
```
Como a queilite glandular pode ser tratada? A queilite glandular geralmente é tratada com corticosteroides.  O tratamento com corticosteroides pode incluir esteróides orais, cremes ou gel de corticosteroides.  Em alguns casos, pode ser necessário o uso de um medicamento imunossupressor.  O tratamento com medicamentos imunossupressores pode incluir ciclosporina, tacrolimus e/ou azatioprina.
```

</details>
