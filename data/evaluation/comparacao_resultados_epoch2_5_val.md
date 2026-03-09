# Comparação: Modelo Base vs Fine-Tuned

**Data:** 2026-03-09 02:53

## Métricas Agregadas

### Sobreposição entre modelos (FT vs Baseline)

| Métrica | Valor |
|---------|-------|
| Comprimento médio (Base) | 1048 chars |
| Comprimento médio (Fine-tuned) | 1086 chars |
| Ratio de comprimento (FT/Base) | 1.19x |
| BLEU Score | 0.0063 |
| ROUGE-1 F1 | 0.1489 |
| ROUGE-2 F1 | 0.0215 |
| ROUGE-L F1 | 0.1013 |

### Qualidade vs Referência (Ground Truth)

| Métrica | Baseline | Fine-Tuned |
|---------|----------|------------|
| BLEU | 0.0388 | 0.0118 |
| ROUGE-1 F1 | 0.3182 | 0.1430 |
| ROUGE-2 F1 | 0.0877 | 0.0290 |
| ROUGE-L F1 | 0.1748 | 0.1020 |
| Similaridade Semântica | 0.9036 | 0.8414 |

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
Qu pessoicaixaica?a Sindactilia tipo  ico tip  icos,   sintomasosiais de pele pálidaado-clar, olhos profundiamentemente inseridosiais-cantos inclin  dobrasa pele fin-espessiais-cant-lábio (cerca  uma milla)ico tip oada síndrome  cefala síndrome/quando a síndrome/qu  síndrome pélvicasíndromeicos-qu/qu/quicaixaicaado icaixaicasíndrome,:sinalicaixaica,, um sinal  o  o
,o   pélvica-ilíaco/pélv-ilíaco/pélv/ilíaco  - ilíaco,a ão-cicatrizes-anormais o um sinal
 - anormalidades,/anormalidade - anormalid...
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
O queilite glandular-ungueite / do/ sinal/icasicaçãos,iaiçaçõesoo sinalicaçãoico é-o trat:     o queilite glandular - ungueite/sinal,dos,do/ sinalssicaçãoico,a os tratico é pior (o-o/a: pioricação/sicaçãoe o,icoão: icônio/imagem icaçãoa: ícon/imagem: sicação-ungueitea (ou/ouicação,, i-c-a-ta-z)eos trats  o queilite glandular iungeiteia-sinal eicação  pioros   os tratico-sintomas   icaçãoico,aicação-sinal-ungueite-os trataoaosos tratico/os sintomas/as icação ciclotimícia sialadenite  - ungueite -...
```

</details>
