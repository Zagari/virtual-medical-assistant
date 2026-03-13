# Comparacao Completa: Baseline vs Epoch 1 vs Epoch 1.5 vs Epoch 2 vs Epoch 2.5 vs Epoch 4 vs Epoch 5 vs es

**Data:** 2026-03-13 12:06
**Modelos avaliados:** 8 (baseline + 7 checkpoints)

## Trilha A — Sobreposicao entre Modelos (50 perguntas manuais)

Metricas calculadas comparando cada modelo fine-tuned com o baseline.

| Metrica | Baseline | FT Epoch 1 | FT Epoch 1.5 | FT Epoch 2 | FT Epoch 2.5 | FT Epoch 4 | FT Epoch 5 | FT es |
|---------|------------|------------|------------|------------|------------|------------|------------|
| Comprimento medio | 1225 chars | 1230 chars | 1256 chars | 1160 chars | 1093 chars | 706 chars | 1254 chars | 1339 chars |
| BLEU vs Baseline | — | 0.0312 | 0.0291 | 0.0022 | 0.0029 | 0.0027 | 0.0245 | 0.0308 |
| ROUGE-1 F1 vs Baseline | — | 0.3007 | 0.3014 | 0.1327 | 0.1469 | 0.2064 | 0.2956 | 0.3056 |
| ROUGE-2 F1 vs Baseline | — | 0.0793 | 0.0795 | 0.0109 | 0.0118 | 0.0113 | 0.0739 | 0.0740 |
| ROUGE-L F1 vs Baseline | — | 0.1704 | 0.1706 | 0.0963 | 0.1024 | 0.1513 | 0.1696 | 0.1739 |
| Taxa de repeticao (3-gramas) | 0.0664 | 0.2676 | 0.2752 | 0.0067 | 0.0057 | 0.0022 | 0.2945 | 0.3360 |

## Trilha B — Qualidade vs Ground Truth (50 amostras validacao MedQuAD)

Metricas calculadas comparando as respostas de cada modelo com a resposta de referencia.

| Metrica | Baseline | FT Epoch 1 | FT Epoch 1.5 | FT Epoch 2 | FT Epoch 2.5 | FT Epoch 4 | FT Epoch 5 | FT es |
|---------|------------|------------|------------|------------|------------|------------|------------|
| BLEU vs Referencia | 0.0388 | 0.2002 | 0.2982 | 0.0042 | 0.0118 | 0.0025 | 0.2168 | 0.2217 |
| ROUGE-1 F1 vs Ref | 0.3182 | 0.4224 | 0.5173 | 0.1249 | 0.1430 | 0.1639 | 0.4403 | 0.4414 |
| ROUGE-2 F1 vs Ref | 0.0877 | 0.2611 | 0.3601 | 0.0211 | 0.0290 | 0.0097 | 0.2750 | 0.2795 |
| ROUGE-L F1 vs Ref | 0.1748 | 0.3367 | 0.4205 | 0.0942 | 0.1020 | 0.1189 | 0.3459 | 0.3451 |
| Similaridade Semantica | 0.9036 | 0.9234 | 0.9393 | 0.8338 | 0.8414 | 0.7780 | 0.9280 | 0.9282 |

## Exemplos Qualitativos (8 modelos lado a lado)

### Sintomas

**Pergunta 1:** Quais são os principais sintomas do diabetes tipo 2?

<details>
<summary>Ver respostas dos 8 modelos</summary>

**Baseline:**
```
Os principais sintomas do diabetes tipo 2 incluem:

1. Sensação de sede e fome constantes, devido à falta de insulina ou a sua ineficácia.
2. Frequentes urinações, especialmente à noite, devido à elevação do nível de glucose no soro sanguíneo que causa o corpo a excretar mais urina.
3. Perda de peso sem qualquer esforço, pois o corpo começa a queimar a energia dos tecidos em vez de armazená-la.
4....
```

**Fine-Tuned Epoch 1:**
```
Os sintomas do diabetes tipo 2 podem incluir:
                
Sintomas de diabetes tipo 1 e tipo 2 podem ser semelhantes, mas o diabetes tipo 1 geralmente começa mais rapidamente.
```

**Fine-Tuned Epoch 1.5:**
```
Os sintomas do diabetes tipo 2 incluem - Increse na micção - Sentir muito fome ou cansaço - Perder peso sem tentar - Feridas de cicatrizamento lento - Tireoide aumentada - Manchas na pele - Dor ou sensibilidade nos pés. Os sintomas podem ser lentos e súbitos e podem variar de pessoa para pessoa. As mulheres podem apresentar um câncer de útero ou de mama. As pessoas afro-americanas podem ter doença...
```

**Fine-Tuned Epoch 2:**
```
Os açúcares -, çãomoglioseicaçãomogliose/gluconeogênese--,o corpo produz çãomogliose um açúcar a ponte, çãomogliosee gluconeogênese sintetizicação çãomogliosea forma o açúcaroiaicação (corao), cérebro çãomogliosee gluconeogênese çãomogliose çãomogliose sintetizada (corpo pálido, peleicação-açúcaricos-, cérebro çãomoglioseicos-çãomogliose, pele çãomogliose çãomoglioseo cérebro--sangue çãomogliose ç...
```

**Fine-Tuned Epoch 2.5:**
```
Esso depend oicaisonomia
ão
a um nívela dos hormôn (a insulinaos um hormônioada qualquer substância, produzida ás células, pesso,/ouão ósso o/icoisos produzido ás células/ada qualquer substância sintetizada ás células   pesso pesso (  os uma substânciaica produzidaica produzida ás células icaisonomica   sintomas   ácele.  Diabetes, tipo -os icaisonomosica icoisica produzida um hormônio uma substân...
```

**Fine-Tuned Epoch 4:**
```
c  que/   de ,ada/ /   або  */想 /  uma (/    //,/ ada, /,-, / ,,//  e o deada( e…  (//想 ( de, ,a e /想,   de/ /,/,   , ,,,,/,,o e /,,  *,/   /ada - sc a c de um,//ada/,ada-/ / або, e  або   de-/ // ada e  /  e , 立/  de  e e,  ( ada-  立,    , c/  e,  que  / ,  ,ado ,,/ ,/,/ / ( , або у/// у de// uma,  de立 /  é e/o,o de,   / que,-  e   / /, ,/  de/  e/… у  e,,/ 想 e de  e,  //,/a/      ,/ada e/,想 e   ...
```

**Fine-Tuned Epoch 5:**
```
Os sinais e sintomas do diabetes tipo 2 incluem urina muito escurecida, sensação de fome e cansaço, visão turva e cicatrizes na pele. A maioria dos sintomas do diabetes tipo 2 não são tão graves quanto os sintomas de diabetes mellitus de início agudo (DMIA), mas pode ser grave se não for tratada. O diabetes tipo 2 geralmente progride lentamente, mas a doença pode causar problemas de saúde e de vid...
```

**Fine-Tuned es:**
```
Quais são os sinais e sintomas do diabetes tipo 2? A Ontologia do Fenótipo Humano fornece a seguinte lista de sinais e sintomas para diabetes mellitus, tipo 2. Se a informação estiver disponível, a tabela abaixo inclui a frequência com que o sintoma é observado em pessoas com esta condição. Você pode usar o Dicionário Médico MedlinePlus para procurar as definições desses termos médicos. Sinais e S...
```

</details>

### Tratamento

**Pergunta 11:** Qual é o tratamento de primeira linha para hipertensão arterial?

<details>
<summary>Ver respostas dos 8 modelos</summary>

**Baseline:**
```
A hipertensão arterial é uma condição médica caracterizada por altos níveis de pressão arterial crônica. O tratamento de primeira linha para hipertensão arterial geralmente envolve a modificação de hábitos de vida e a utilização de medicamentos.

A modificação de hábitos de vida pode incluir:

1. Redução do peso em pessoas que são sobrepesas ou obesas.
2. Redução do consumo de sal.
3. Exercício re...
```

**Fine-Tuned Epoch 1:**
```
A hipertensão arterial é tratada com medicamentos e mudanças no estilo de vida. Muitos medicamentos são usados ​​para tratar a hipertensão arterial. A maioria deles controla a pressão arterial em um ou dois dos três sistemas. Muitos tratamentos são usados ​​em combinação.
                
Muitos medicamentos para pressão arterial podem ser usados ​​por pessoas com diabetes e/ou doença renal.
     ...
```

**Fine-Tuned Epoch 1.5:**
```
Para pessoas com pressão alta, o objetivo do tratamento é reduzir a pressão arterial e reduzir o risco de doenças cardíacas, acidente vascular cerebral, insuficiência renal e outras complicações da doença. 
                
A pressão arterial normal é uma pressão arterial de 120/80 mmHg. A pressão arterial elevada é uma pressão arterial superior a 140/90 mmHg.
```

**Fine-Tuned Epoch 2:**
```
As opções-trat/trataicaisaçõesiaversãoe/traticosméd sinaisicaisadores sangue iobex, 2//sangue (IOB) icaisosmecaicais  pesso,/tratam/traticais a hipertens sionistação uma forma-trat/trat - o trat/trat --  adação um estudo,aos/icais  /trat, sinaliça/trat sialicais  icosmecaicaisadaçãoicosmecaicais icosmecaicais icosmecaicaissinaliça/trata da hipertensção arterial,esperaadaçãoaos,icosmecaicais uma fo...
```

**Fine-Tuned Epoch 2.5:**
```
A hipertens-tensação arterial  - estão lig - é uma condiçãoicação-o,, piora-sees sintomas- (hipertensicação, sintomas- piorsaídeaa) sintomas, icação ão oico (hipertens/caçãosaídea
,,/cação ão crescimento--icosicoiasíde oicoada) icosio uma condiçãoicação,o-icoicaçãoico-crescimento icação ão crescimentoicação icosio-crescimentoos crescimento sintomas,esicação ão crescimento icosioão crescimento icos...
```

**Fine-Tuned Epoch 4:**
```
uma  eada  / o/ de  e c…/ de c… , de… c c-o,/o umaado  cc * ada/ ,  e ,,/s/ (ada/,//  uma  (  o/,, e,/  想   e/,   /   e, ,/   e , ado,   ada/ é /c  e-   想 e, ,  /立 ado  e ,a  ,  - ,, uma  de(想  / (/, e  que     ,   - ,想 /   / eica////// (  立 /- (ado    e que  ,, / у/ uma,,o// e … que e,/ де    e/-/ o ( у / é e s ado que/想,   ada,/, /,  або де-   ( adaica /, або  de  , // де /, eado/,/// uma/ *//  ...
```

**Fine-Tuned Epoch 5:**
```
O tratamento de primeira linha para hipertensão arterial é um medicamento chamado diurético. O diurético é um medicamento que ajuda a remover o líquido extra do corpo. É usado para tratar a hipertensão arterial porque reduz a pressão arterial e limita os efeitos colaterais dos outros medicamentos usados ​​para tratar a pressão alta. O diurético pode ser administrado por via oral ou intravenosa.
```

**Fine-Tuned es:**
```
A hipertensão arterial (HA) pode ser tratada com mudanças no estilo de vida, medicamentos ou ambos.
                
Mudanças no estilo de vida. Mudanças no estilo de vida são um tratamento para hipertensão arterial que pode ajudar a diminuir a pressão arterial e prevenir o aumento da pressão arterial no futuro. Uma mudança no estilo de vida pode incluir:
                
Eliminar ou reduzir o tab...
```

</details>

### Medicamentos

**Pergunta 21:** Quais são os efeitos colaterais da metformina?

<details>
<summary>Ver respostas dos 8 modelos</summary>

**Baseline:**
```
A metformina é um medicamento usado principalmente para o tratamento do diabetes tipo 2. Alguns efeitos colaterais comuns da metformina podem incluir:

1. Náusea e vômito: Estes sintomas podem ocorrer no início do tratamento, mas geralmente se dissipam com o tempo.
2. Diarreia: Em alguns casos, a metformina pode causar diarreia, especialmente se a dose é aumentada rapidamente.
3. Tontura: Alguns p...
```

**Fine-Tuned Epoch 1:**
```
A metformina pode causar efeitos colaterais comuns e leves. Os efeitos colaterais mais comuns incluem diarreia, náuseas e vômitos. A maioria dos sintomas geralmente desaparece com o tempo. Se você tiver diarreia, você pode tomar a metformina depois de comer. Além disso, você pode tentar tomar um dosados mais baixo para começar. Você também pode tentar tomar metformina ao mesmo tempo com um inibido...
```

**Fine-Tuned Epoch 1.5:**
```
Quais são os efeitos colaterais da metformina? A maioria das pessoas tolera bem a metformina, mas alguns podem sentir efeitos colaterais. Os efeitos colaterais mais comuns da metformina incluem: - diarreia - dor abdominal - gases - náuseas e vômitos - dor de cabeça - inchaço dos pés e tornozelos - cansaço A diarreia é o efeito colateral mais comum. Os efeitos colaterais podem ser reduzidos esvazia...
```

**Fine-Tuned Epoch 2:**
```
Quaisçãois/-esicaisadores, ursinais ursodianaise dor/dor de estômago ursodianaise, ursodianaise ursodianaise
- cálcul ursodianaise ursodianaiseo ursodianaise/cálculicais (cálcul ursodianaise ursodianaise,icais, o pâncreasico ursodianaise cálcul ursodianaise/cálculicais, dor,diarréoseso-diarréos ursodianaises (diarréia ursodianaiseoa-diarréçãoicais ursodianaise: dorada, diarréada, gaseosita sintoma...
```

**Fine-Tuned Epoch 2.5:**
```
A metforminaaument-loicazeleta o corpo/blood-glucose.  A metforminasão-jejunal icoza/bloodada metforminaicoza-glucosida/glicosea metforminaica. sintomaicoza  icazaicosmetizam-seicaz-se  sintomaiaument/descrevericosmetizica icoso/glucoss-es sintomas um dos cresciment sintomassintomaaument /descrever/metamorfose /metamorfose /metamorfoseaument  /descrever um-çãosintomao/metamorfose/metamorfose-sinto...
```

**Fine-Tuned Epoch 4:**
```
a é e/ або,//想 uma/,/, /    e/   у立   // // ,c *,, de ,  oado у eada/a,,,/,-  de  ,  / / ada / e,  ( de / ,, ada /  - de у      абоa que / e c/,/ , ,/o想ada e   que//立 ca/   / -   /,…想 /// /,   ,///    ada/ ,s /,///-ada/ //- umaada/ *, …,  -立 que,      у, e c *ado  o /ada/-, у ,/  /o umaado//ada  uma,/ ,ado, ,, de-  o/ é /,/,  -, ( ,  /( або e 立 абоoa   s ,想-//c…想/    de  /  / que, у/  або /    ( /...
```

**Fine-Tuned Epoch 5:**
```
Os efeitos colaterais da metformina podem incluir:
                
Gastrointestinal. A maioria dos efeitos colaterais da metformina é gastrointestinal, incluindo diarreia e vômito. Os efeitos gastrointestinais geralmente se desenvolvem dentro de alguns dias após o início do tratamento com metformina e geralmente desaparecem dentro de alguns dias após o início do tratamento. Os efeitos gastrointes...
```

**Fine-Tuned es:**
```
A metformina pode causar os seguintes efeitos colaterais. Os efeitos colaterais geralmente desaparecem com o tempo.
                
- diarreia ou outros problemas digestivos - náuseas - vômitos - dor de estômago - tonturas - cãibras musculares ou articulares - fraqueza - sensação de cansaço - dificuldade para dormir - dores de cabeça
                
O seu médico poderá recomendar que você comece...
```

</details>

### Prevencao

**Pergunta 31:** Como prevenir o diabetes tipo 2?

<details>
<summary>Ver respostas dos 8 modelos</summary>

**Baseline:**
```
Ao prevenir o diabetes tipo 2 é importante seguir uma dieta equilibrada, com 50% de carboidratos, 25% de gorduras e 25% de proteínas. Além disso, é importante fazer exercício físico regular, com pelo menos 30 minutos por dia, 5 dias por semana. É recomendável evitar a sedentariedade, manter um peso saudável e reduzir o consumo de açúcar, gorduras saturadas e sal. É importante também fazer testes r...
```

**Fine-Tuned Epoch 1:**
```
Não é possível prevenir o diabetes tipo 2, mas você pode atrasar ou prevenir a doença em um estágio precoce. A prevenção é especialmente importante para pessoas que tenham histórico familiar da doença, que tenham um peso elevado ou que tenham outras condições de saúde que aumentem o risco de diabetes tipo 2.
                
Se você tem diabetes tipo 2, pode atrasar ou prevenir a complicação do di...
```

**Fine-Tuned Epoch 1.5:**
```
Não existe tratamento para prevenir o diabetes tipo 2, mas você pode tomar medidas para reduzir os riscos de desenvolver a doença.
                
Se você tem diabetes, pode prevenir ou retardar problemas relacionados ao diabetes, como doenças cardíacas, doenças renais e problemas oculares. Isso pode ajudá-lo a viver mais tempo e melhor.
                
Pontos-chave
                
- Você pode ...
```

**Fine-Tuned Epoch 2:**
```
A perdaicação e exercícioado ajud icação a reduziricaçãosicaçãoes / ris, espaç uma vezicação/dia  aumento  pancreas o produção pancreasa produção/diabetes,  oicasação
 icoisação/diabetes ocorre/aumenticoisação um aument  pancreas/diabetessuspeita içançaço de diabetes icoisação-diabetes icoisaçãoaumentosuspeita/diabetes:- exercícião/diabetes içançaço  (ou -exercíciãoesaçaço-diabetes-exercícião,-exe...
```

**Fine-Tuned Epoch 2.5:**
```
Um estilo um pouco mais saudável-
/nosso estilo/index um pouicaixa  a-Estilo um poucaixa /nosso estilo-indexsaude-este-estiloa-Estilo um poucaixa-Estilo um poucaixaoicoso estilo-index , oo-ko-so/Estiloa o,icax pessossaude-esteicax ada-Estilo-um-poucaixaa-Estilo/Estilo-um-poucaixa-Estilo ,e-stilaada-Estilo-um:-Estilo ,
 súbe/suba pesso pessoicaixasaude/Estiloicaixasaude ,a,icax a-Estilo os um pouos...
```

**Fine-Tuned Epoch 4:**
```
,, ,o /ado   e- //ica o /立-  / uma  é立o/  * /   /ada/ / é c   -   de ada/o,  , ,- або  o - ,-  uma adoo  (  e /  *立,  де /, у// - ( que  / de або     / у  (   e//  想/想想ada, / c    um,, у    /- que立 / /   ,      de , ado uma/ ( / um,ado/ /  /ada- ,- 立// e uma e  s ,/ que/ a, uma / de /想,,, /a/  у 想  adaado  ,,  c / a// é    uma/aa,  ,ica umado  //- / é ,,ada * ,,  у ada  або  uma (,ado ado de  /,/ ...
```

**Fine-Tuned Epoch 5:**
```
A prevenção do diabetes tipo 2 começa com uma boa controle do peso. A perda de peso pode ajudar a prevenir ou retardar o diabetes tipo 2. Mantenha um peso saudável. Mantenha o peso corporal (imc) abaixo de 25. Você pode descobrir seu imc usando um calculador online ou aplicativo. Você também pode usar o calculador de imc do Instituto Nacional de Diabetes e Doenças Digestivas e Renais. Você pode de...
```

**Fine-Tuned es:**
```
A prevenção do diabetes tipo 2 se concentra em reduzir os riscos de desenvolver o doença. Os riscos de desenvolver o diabetes tipo 2 incluem
                
- ser obeso - ter histórico familiar - ter histórico pessoal - ter níveis elevados de açúcar no sangue (glicose) - ter níveis elevados de triglicerídeos ou colesterol no sangue - não ser ativo - ter histórico de hipertensão - ter hipertensão ...
```

</details>

### Emergencias

**Pergunta 41:** O que fazer em caso de suspeita de AVC?

<details>
<summary>Ver respostas dos 8 modelos</summary>

**Baseline:**
```
Caso haja suspeita de acidente vascular cerebral (AVC), é essencial agir de forma rápida para minimizar os danos potencialmente causados. A seguinte é uma lista de etapas que devem ser seguidas:

1. Chame o serviço de emergência imediatamente: Ligue para o serviço de ambulância local ou, se necessário, para o hospital mais próximo.

2. Acompanhe as instruções do operador de emergência: O operador ...
```

**Fine-Tuned Epoch 1:**
```
- Um acidente vascular cerebral (AVC) ocorre quando o fluxo sanguíneo para o cérebro é interrompido por um coágulo sanguíneo, um bloqueio ou uma ruptura de uma artéria.  - O tratamento para AVC é mais eficaz quando for administrado na primeira hora após o início dos sintomas.  - Os sintomas de AVC incluem tonturas, dor de cabeça, dificuldade para fala, paralisia de um lado do corpo e visão dupla. ...
```

**Fine-Tuned Epoch 1.5:**
```
- Um acidente vascular cerebral (AVC) ocorre quando o fluxo sanguíneo para o cérebro é interrompido ou bloqueado.  - O AVC é um problema médico grave que requer tratamento imediato.  - Uma pessoa que apresenta sintomas de AVC deve ligar para o 9-1-1 imediatamente para solicitar atendimento médico de emergência.  - Uma pessoa que acredita que alguém está tendo um AVC deve ligar para o 9-1-1 imediat...
```

**Fine-Tuned Epoch 2:**
```
Aindaica como rápida e rica em oxigênio-   pílulas sólidaso sódio oximetra.  um test, adaquiros,  ,ica. -  ligado um númerosério
 um número ção oximetra icaa.,ica,oçanhãossólidasica sódio ica oximetraicosárias icaação ica-: cânhãos,icao icaespeçãoica/exame ica um número oximetra uma pílula/pílula ica,ica- um testica,icaão ica,icaão,ica ica icaaa./ica: cânhão uma pílulao oximetra,ica oximetra ica-a...
```

**Fine-Tuned Epoch 2.5:**
```
O trat-amento pior,ção rápidaa suspeita ,:, :-icoso-toma um medicamento-tome um medicamentoado,    ,-de-bloqueador espera-a-quatro-aadoes um medicamentoa medicamento   a-doado /suspeita/trates,suspeita---do, -quatro ico-sotime-medicamento suspeita o-oo o-do súspeita, uma das princip/principicais caus s,a-do oicaisonaçãoo-do-suspeita,suspeita icososotimeção ada-do,/trat/trat suspeita -quatro-aadao,...
```

**Fine-Tuned Epoch 4:**
```
umaada  queada / /  / або/, ,icaado/ ,o立 або//ada//    o   e o//-  /ado/a, ica      uma, …  ada  é/ de,o um,  o a *//     (, //o  / oo   - ,/ ,//a,,ada de  / * e,/ /    /   / /想 uma ado/ /,  *   … ( або ada/ /,/(   / e,ada o,   / c/ uma- é, уica e  /o/  (//-ada e/   e/- c / / -/ica想 eo / /  de  /-   ,  / c  / *, // e ,… / *//    ( ,/ c    /   deado- , / (ada -, e  / ,  - es,,/ / ,  e     ,/ / ,  ,...
```

**Fine-Tuned Epoch 5:**
```
Se você estiver suspeitando de um ataque isquêmico transitório (AIT), ligue para o 9-1-1 imediatamente. Não espere por mais sinais ou sintomas. O tratamento do AIT é o mesmo que o tratamento do acidente vascular cerebral. Você pode precisar de medicamentos para tratar o AVC e prevenir a recorrência. A maioria dos medicamentos que são úteis para prevenir um acidente vascular cerebral são seguros pa...
```

**Fine-Tuned es:**
```
- O ataque isquêmico transitório (AIT) é um sintoma de um derrame a caminho de ocorrer. Um AIT pode ser um aviso que um derrame está a ocorrer ou pode acontecer no futuro.  - Os sintomas de um AIT incluem - Dor de cabeça - Dor de cabeça - Dor de cabeça - Dor de cabeça - Dor de cabeça - Dor de cabeça - Dor de cabeça - Dor de cabeça - Dor de cabeça - Dor de cabeça - Dor de cabeça - Dor de cabeça - D...
```

</details>

## Recomendacao

Com base nos resultados acima, a recomendacao sera preenchida apos analise dos dados.
