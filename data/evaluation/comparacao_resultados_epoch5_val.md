# Comparação: Modelo Base vs Fine-Tuned

**Data:** 2026-03-09 05:30

## Métricas Agregadas

### Sobreposição entre modelos (FT vs Baseline)

| Métrica | Valor |
|---------|-------|
| Comprimento médio (Base) | 1048 chars |
| Comprimento médio (Fine-tuned) | 981 chars |
| Ratio de comprimento (FT/Base) | 0.97x |
| BLEU Score | 0.0424 |
| ROUGE-1 F1 | 0.3118 |
| ROUGE-2 F1 | 0.0990 |
| ROUGE-L F1 | 0.1821 |

### Qualidade vs Referência (Ground Truth)

| Métrica | Baseline | Fine-Tuned |
|---------|----------|------------|
| BLEU | 0.0388 | 0.2168 |
| ROUGE-1 F1 | 0.3182 | 0.4403 |
| ROUGE-2 F1 | 0.0877 | 0.2750 |
| ROUGE-L F1 | 0.1748 | 0.3459 |
| Similaridade Semântica | 0.9036 | 0.9280 |

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
Quais são os sinais e sintomas da Sindactilia tipo 3? A Ontologia do Fenótipo Humano fornece a seguinte lista de sinais e sintomas para Sindactilia tipo 3. Se a informação estiver disponível, a tabela abaixo inclui a frequência com que o sintoma é observado em pessoas com esta condição. Você pode usar o Dicionário Médico MedlinePlus para procurar as definições desses termos médicos. Sinais e sintomas Número aproximado de pacientes (quando disponível) Anormalidade do tórax 90% Anormalidade do pav...
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
Como a queilite glandular pode ser tratada? O tratamento da queilite glandular pode incluir: medicamentos antimicrobianos, como amoxicilina ou azitromicina; corticosteroides; medicamentos imunomoduladores, como ciclofosfamida; e/ou cirurgia. Embora esta condição seja muito rara, a cirurgia pode ser recomendada para casos graves. A cirurgia pode incluir a remoção dos gânglios linfáticos do rosto e/ou remoção de um ou mais gânglios linfáticos.
```

</details>
