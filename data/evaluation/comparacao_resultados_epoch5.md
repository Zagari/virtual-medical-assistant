# Comparação: Modelo Base vs Fine-Tuned

**Data:** 2026-03-09 05:02

## Métricas Agregadas

### Sobreposição entre modelos (FT vs Baseline)

| Métrica | Valor |
|---------|-------|
| Comprimento médio (Base) | 1225 chars |
| Comprimento médio (Fine-tuned) | 1254 chars |
| Ratio de comprimento (FT/Base) | 1.13x |
| BLEU Score | 0.0245 |
| ROUGE-1 F1 | 0.2956 |
| ROUGE-2 F1 | 0.0739 |
| ROUGE-L F1 | 0.1696 |

## Comparação por Categoria

### Sintomas

**Pergunta 1:** Quais são os principais sintomas do diabetes tipo 2?

<details>
<summary>Ver respostas</summary>

**Resposta do Modelo Base:**
```
Os principais sintomas do diabetes tipo 2 incluem:

1. Sensação de sede e fome constantes, devido à falta de insulina ou a sua ineficácia.
2. Frequentes urinações, especialmente à noite, devido à elevação do nível de glucose no soro sanguíneo que causa o corpo a excretar mais urina.
3. Perda de peso sem qualquer esforço, pois o corpo começa a queimar a energia dos tecidos em vez de armazená-la.
4. Cansaço excessivo, pois o corpo precisa esforçar-se para compensar a falta de insulina.
5. Feridas ...
```

**Resposta do Modelo Fine-Tuned:**
```
Os sinais e sintomas do diabetes tipo 2 incluem urina muito escurecida, sensação de fome e cansaço, visão turva e cicatrizes na pele. A maioria dos sintomas do diabetes tipo 2 não são tão graves quanto os sintomas de diabetes mellitus de início agudo (DMIA), mas pode ser grave se não for tratada. O diabetes tipo 2 geralmente progride lentamente, mas a doença pode causar problemas de saúde e de vida.
```

</details>

**Pergunta 2:** Quais são os sinais de alerta de um infarto agudo do miocárdio?

<details>
<summary>Ver respostas</summary>

**Resposta do Modelo Base:**
```
Um infarto agudo do miocárdio (IAM) é um evento grave que ocorre quando o fluxo sanguíneo para o miocárdio é interrompido, causando uma necrose (morte) de células do miocárdio. Ao longo do tempo, os sinais e sintomas do IAM podem variar, mas alguns sinais de alerta comuns incluem:

1. Dor no peito: a dor pode ser descrita como uma dor forte, pesada, pressurizada ou apertada que dura mais de 15 minutos. A dor pode ser localizada no centro do peito, no lado esquerdo, no lado direito, ou em ambos o...
```

**Resposta do Modelo Fine-Tuned:**
```
Sinais de alerta de um IAM incluem dores de peito, falta de ar, dores de cabeça e vômitos. Sinais de alerta de um IAM incluem dor no peito, falta de ar, dores de cabeça e vômitos. A dor no peito é a mais comum. Ela pode se assemelhar a uma dor de puxado no peito. A dor no peito pode ser descrita como - dor aguda e intenso - dor que piora com o exercício - dor que piora durante o repouso - dor no peito que piora ao estendê-lo - dor no peito que melhora com medicamentos - dor no peito que se espal...
```

</details>

### Tratamento

**Pergunta 11:** Qual é o tratamento de primeira linha para hipertensão arterial?

<details>
<summary>Ver respostas</summary>

**Resposta do Modelo Base:**
```
A hipertensão arterial é uma condição médica caracterizada por altos níveis de pressão arterial crônica. O tratamento de primeira linha para hipertensão arterial geralmente envolve a modificação de hábitos de vida e a utilização de medicamentos.

A modificação de hábitos de vida pode incluir:

1. Redução do peso em pessoas que são sobrepesas ou obesas.
2. Redução do consumo de sal.
3. Exercício regular.
4. Redução do consumo de bebidas alcoólicas.
5. Redução do consumo de café e chá.
6. Alteraçõ...
```

**Resposta do Modelo Fine-Tuned:**
```
O tratamento de primeira linha para hipertensão arterial é um medicamento chamado diurético. O diurético é um medicamento que ajuda a remover o líquido extra do corpo. É usado para tratar a hipertensão arterial porque reduz a pressão arterial e limita os efeitos colaterais dos outros medicamentos usados ​​para tratar a pressão alta. O diurético pode ser administrado por via oral ou intravenosa.
```

</details>

**Pergunta 12:** Como é feito o tratamento da diabetes tipo 2?

<details>
<summary>Ver respostas</summary>

**Resposta do Modelo Base:**
```
O tratamento da diabetes tipo 2 é geralmente baseado em três pilares fundamentais: alterações de estilo de vida, medicamentos e controle da dieta.

1. Alterações de estilo de vida:
   - Exercício físico regular: 30 minutos por dia, 5 dias por semana, de preferência em períodos contínuos.
   - Perda de peso: para pessoas que estão acima do peso ideal, uma perda de 5-7% do peso corporal pode ajudar a controlar a diabetes.
   - Não fumar: para pessoas que fumam, deixar de fumar pode melhorar a cond...
```

**Resposta do Modelo Fine-Tuned:**
```
O tratamento do diabetes tipo 2 geralmente se concentra no controle do açúcar no sangue. O tratamento pode envolver alterações no estilo de vida, medicamentos e/ou insulina. Algumas pessoas podem precisar usar mais de um tratamento.
                
Muitos tratamentos estão disponíveis para tratar o diabetes tipo 2. O seu médico pode recomendar um ou mais dos seguintes:
                
- mudanças no estilo de vida - medicamentos - insulina - cirurgia - transplante de células pancreáticas - tera...
```

</details>

### Medicamentos

**Pergunta 21:** Quais são os efeitos colaterais da metformina?

<details>
<summary>Ver respostas</summary>

**Resposta do Modelo Base:**
```
A metformina é um medicamento usado principalmente para o tratamento do diabetes tipo 2. Alguns efeitos colaterais comuns da metformina podem incluir:

1. Náusea e vômito: Estes sintomas podem ocorrer no início do tratamento, mas geralmente se dissipam com o tempo.
2. Diarreia: Em alguns casos, a metformina pode causar diarreia, especialmente se a dose é aumentada rapidamente.
3. Tontura: Alguns pacientes podem sentir tontura após tomar a metformina.
4. Dores abdominais: Estes sintomas geralment...
```

**Resposta do Modelo Fine-Tuned:**
```
Os efeitos colaterais da metformina podem incluir:
                
Gastrointestinal. A maioria dos efeitos colaterais da metformina é gastrointestinal, incluindo diarreia e vômito. Os efeitos gastrointestinais geralmente se desenvolvem dentro de alguns dias após o início do tratamento com metformina e geralmente desaparecem dentro de alguns dias após o início do tratamento. Os efeitos gastrointestinais podem ser reduzidos pela ingestão de dieta rica em fibras e aumentando lentamente a dose da m...
```

</details>

**Pergunta 22:** Quais são as contraindicações do uso de AAS (aspirina)?

<details>
<summary>Ver respostas</summary>

**Resposta do Modelo Base:**
```
As contraindicações para o uso de AAS (aspirina) incluem:

1. Alergia à aspirina ou outros antiinflamatórios não esteroides (NSAIDs).
2. Hemofilia ou outras condições que aumentam o risco de sangramento.
3. Dificuldade de coagulação do sangue.
4. Cirrose hepática ativa.
5. Insuficiência renal grave.
6. Doenças do trato gastrointestinal (GI), como úlceras, gastrite erosiva ou colites.
7. Gravidez ou amamentação.
8. Condições cardiovasculares, como infarto do miocárdio agudo ou insuficiência cardí...
```

**Resposta do Modelo Fine-Tuned:**
```
Não recomendado na gravidez.  Aspirina pode causar dor no peito, insuficiência cardíaca, sangramento no cérebro, insuficiência renal e sangramento anormal no sistema reprodutor.  O uso de aspirina pode causar hemorragia no sistema reprodutor em homens.  A aspirina não é recomendada para pessoas com insuficiência renal.
```

</details>

### Prevencao

**Pergunta 31:** Como prevenir o diabetes tipo 2?

<details>
<summary>Ver respostas</summary>

**Resposta do Modelo Base:**
```
Ao prevenir o diabetes tipo 2 é importante seguir uma dieta equilibrada, com 50% de carboidratos, 25% de gorduras e 25% de proteínas. Além disso, é importante fazer exercício físico regular, com pelo menos 30 minutos por dia, 5 dias por semana. É recomendável evitar a sedentariedade, manter um peso saudável e reduzir o consumo de açúcar, gorduras saturadas e sal. É importante também fazer testes regulares de glicemia e consultar um médico se houver sintomas ou dúvidas. Ainda é importante evitar ...
```

**Resposta do Modelo Fine-Tuned:**
```
A prevenção do diabetes tipo 2 começa com uma boa controle do peso. A perda de peso pode ajudar a prevenir ou retardar o diabetes tipo 2. Mantenha um peso saudável. Mantenha o peso corporal (imc) abaixo de 25. Você pode descobrir seu imc usando um calculador online ou aplicativo. Você também pode usar o calculador de imc do Instituto Nacional de Diabetes e Doenças Digestivas e Renais. Você pode descobrir mais sobre o imc no site do Instituto Nacional de Saúde do Consumidor.
                
Você...
```

</details>

**Pergunta 32:** Quais são as medidas de prevenção de doenças cardiovasculares?

<details>
<summary>Ver respostas</summary>

**Resposta do Modelo Base:**
```
As medidas de prevenção de doenças cardiovasculares podem ser resumidas em vários aspectos, que abrangem a alimentação, a atividade física, o estilo de vida, o controle de riscos e o tratamento de condições pré-existentes.

1. Alimentação saudável: Consumir uma dieta rica em frutas, verduras, cereais integrais, proteínas de origem vegetal e animal, óleos saudáveis (como óleo de oliva e noz) e limitar o consumo de alimentos ricos em gordura saturada, sal e açúcar adicionado.

2. Atividade física:...
```

**Resposta do Modelo Fine-Tuned:**
```
Sua dieta pode afetar a saúde do seu coração. Você pode reduzir o risco de doenças cardíacas e outros problemas de saúde com um plano alimentar saudável. NIH: Instituto Nacional do Coração, Pulmão e Sangue
```

</details>

### Emergencias

**Pergunta 41:** O que fazer em caso de suspeita de AVC?

<details>
<summary>Ver respostas</summary>

**Resposta do Modelo Base:**
```
Caso haja suspeita de acidente vascular cerebral (AVC), é essencial agir de forma rápida para minimizar os danos potencialmente causados. A seguinte é uma lista de etapas que devem ser seguidas:

1. Chame o serviço de emergência imediatamente: Ligue para o serviço de ambulância local ou, se necessário, para o hospital mais próximo.

2. Acompanhe as instruções do operador de emergência: O operador deve te orientar sobre as medidas a serem tomadas, como manter o paciente reclinado e aplicar uma ba...
```

**Resposta do Modelo Fine-Tuned:**
```
Se você estiver suspeitando de um ataque isquêmico transitório (AIT), ligue para o 9-1-1 imediatamente. Não espere por mais sinais ou sintomas. O tratamento do AIT é o mesmo que o tratamento do acidente vascular cerebral. Você pode precisar de medicamentos para tratar o AVC e prevenir a recorrência. A maioria dos medicamentos que são úteis para prevenir um acidente vascular cerebral são seguros para pessoas que tiveram um AIT e não apresentam sinais e sintomas do AVC.   Consulte o Guia de Pronún...
```

</details>

**Pergunta 42:** Como proceder em uma parada cardiorrespiratória?

<details>
<summary>Ver respostas</summary>

**Resposta do Modelo Base:**
```
Uma parada cardiorrespiratória é uma emergência médica grave que requer intervenção imediata. Aqui estão algumas etapas básicas para ajudar alguém que esteja sofrendo de uma parada cardiorrespiratória:

1. Verifique se o indivíduo realmente está inconsciente e não tem pulso.
2. Se o indivíduo não tiver pulso, comece a dar pressão cardíaca (CPR). O procedimento básico de CPR consiste em dar pressões no tórax do indivíduo, alternando com ventilações nas narinas ou boca do indivíduo.
3. Se o indiví...
```

**Resposta do Modelo Fine-Tuned:**
```
O tratamento para uma parada cardiorrespiratória (PCR) inclui - Reanimação cardiopulmonar (RCP) - Medicamentos - Oxigenoterapia - Tratamento para a causa subjacente - Observação de risco de recorrência - Tratamento de risco de recorrência - Desconexão e palliativismo A RCP é um tratamento de emergência para pessoas que têm um cardio-respiratório (CR) ou outro tipo de PCR.  Os objetivos da RCP são restaurar o ritmo cardíaco e restaurar o fluxo sanguíneo para o cérebro e outros órgãos.  O tratamen...
```

</details>
