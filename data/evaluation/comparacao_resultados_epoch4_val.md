# Comparação: Modelo Base vs Fine-Tuned

**Data:** 2026-03-09 04:25

## Métricas Agregadas

### Sobreposição entre modelos (FT vs Baseline)

| Métrica | Valor |
|---------|-------|
| Comprimento médio (Base) | 1048 chars |
| Comprimento médio (Fine-tuned) | 707 chars |
| Ratio de comprimento (FT/Base) | 0.78x |
| BLEU Score | 0.0029 |
| ROUGE-1 F1 | 0.1944 |
| ROUGE-2 F1 | 0.0114 |
| ROUGE-L F1 | 0.1378 |

### Qualidade vs Referência (Ground Truth)

| Métrica | Baseline | Fine-Tuned |
|---------|----------|------------|
| BLEU | 0.0388 | 0.0025 |
| ROUGE-1 F1 | 0.3182 | 0.1639 |
| ROUGE-2 F1 | 0.0877 | 0.0097 |
| ROUGE-L F1 | 0.1748 | 0.1189 |
| Similaridade Semântica | 0.9036 | 0.7780 |

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
/ / ,ada-/  ada,  um,ado/ ///// c/  uma e   … e, é  /a/ e/ado  uma, é  que, ,- / -,,   a/ um  um   umaica/, e,- 想- * *想, e/ado   //ada,   de,  queo  / ,,/ica que  деo /  * -  (/, é cado queada//,   / e  -   ,/, ,(, ada/  uma… - a c,a    uma/ /s deada    * , у у,, adaada /   / c/,  e/ ( que ( - … queada  -,,,/  e,/ /ada /, /想,//, ( de立, ,, / de    de   uma ica  que  e / -,-/,,  e(- *o ada ,   , ,ada想   e  - *  у / ada ,/ada  oada  um, que  s   e- deado e //,  / ,,  або   /  , у /  uma//-/ /, de/,...
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
ada,,/ uma adaadoica de *  /   es e  é es - que/   /,   / que e uma  (  e  -,/ / eada у /ada або, 想//, eada  uma/ * que ada  /, ada/ de é/adaa que,,  / de,//ado / uma  у,s , e, у //  立    e  de/, ,立ada ,/ada у que e/, -    /(// ,,o  icaada  (ado  de de  (, ,/ oo c/-想,,   ada ado c у de-     ( e/, c ,/,,o,,/,- /ada ,, …-,  ,, a c  ,想o e// , (, /-立/立 у/,  ,, /立   ada/  /ica/  e, у  o  у/ ,/ ,o /   e  ,ada  (  o /, de , o/ s у  de/ 立- cado, e/ / де ada , , 想, o想 або/ o/, ,, c ,,  uma…ada,/,,/… dead...
```

</details>
