# Comparação: Modelo Base vs Fine-Tuned

**Data:** 2026-03-09 01:23

## Métricas Agregadas

### Sobreposição entre modelos (FT vs Baseline)

| Métrica | Valor |
|---------|-------|
| Comprimento médio (Base) | 1048 chars |
| Comprimento médio (Fine-tuned) | 1215 chars |
| Ratio de comprimento (FT/Base) | 1.32x |
| BLEU Score | 0.0038 |
| ROUGE-1 F1 | 0.1370 |
| ROUGE-2 F1 | 0.0185 |
| ROUGE-L F1 | 0.1007 |

### Qualidade vs Referência (Ground Truth)

| Métrica | Baseline | Fine-Tuned |
|---------|----------|------------|
| BLEU | 0.0388 | 0.0042 |
| ROUGE-1 F1 | 0.3182 | 0.1249 |
| ROUGE-2 F1 | 0.0877 | 0.0211 |
| ROUGE-L F1 | 0.1748 | 0.0942 |
| Similaridade Semântica | 0.9036 | 0.8338 |

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
Quais sinaissado sintomas icasiaisicosiaisicaudaleitãoicaudal,icaudaladaicaudal sindactilia de tiposindactilia  um tipo-çãoal,icaudalositônico um tipo:icaudal,icaudal  sindactiliasindactilia/caudal,icaudal-sindactilia  sintomasicaudal,icaudalicocele  sintomas de tipo -caudal o,icaudal o/caudal (caudadaicaudal espinhal -caudal/caudiacocele  aãocaudal,icaudal-sindactilia-caudal-caudala -caudalsindactilia   çãoal-caudalsindactilia:caudalicoceleicaudaleitãoicaudalicaudal,icaudal/caudalicaudal/caudal...
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
Essiais estes recurs,,  pessoes (incluindo pacientes , familiares  , e profissionais-assistentesicaresores).adoçãoicaresores-pacientesoos-pacientes  icaresores   os traticais-pacientes/familiares-icareos pessoicares/profissionais oos-pacientes -ficção/históriasoos-pacientes uma lista /guiaão guiação lista -tratamenta. : -tratamentado/tratament/tratamento,   a,icoresiaão guiaicos a icosos icares-pacientesicares cromo-fotossintetizado  cromoa.espaçoaos sintetizado -tratament um tratamentoicares   ...
```

</details>
