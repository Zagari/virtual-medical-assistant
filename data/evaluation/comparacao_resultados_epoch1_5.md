# Comparação: Modelo Base vs Fine-Tuned

**Data:** 2026-03-08 23:26

## Métricas Agregadas

### Sobreposição entre modelos (FT vs Baseline)

| Métrica | Valor |
|---------|-------|
| Comprimento médio (Base) | 1225 chars |
| Comprimento médio (Fine-tuned) | 1256 chars |
| Ratio de comprimento (FT/Base) | 1.09x |
| BLEU Score | 0.0291 |
| ROUGE-1 F1 | 0.3014 |
| ROUGE-2 F1 | 0.0795 |
| ROUGE-L F1 | 0.1706 |

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
Os sintomas do diabetes tipo 2 incluem - Increse na micção - Sentir muito fome ou cansaço - Perder peso sem tentar - Feridas de cicatrizamento lento - Tireoide aumentada - Manchas na pele - Dor ou sensibilidade nos pés. Os sintomas podem ser lentos e súbitos e podem variar de pessoa para pessoa. As mulheres podem apresentar um câncer de útero ou de mama. As pessoas afro-americanas podem ter doenças cardíacas e do vaso sanguíneo ou doenças renais. As pessoas asiático-americanas, indianas e do Pac...
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
Muitas pessoas que têm ataque cardíaco apresentam dor ou desconforto no peito, mas outros sintomas podem incluir: - dor ou desconforto nas costas, braços, pescoço, mandíbula ou garganta - dor ou desconforto no peito que desaparece e voltar - respiração anormal ou dificuldade para respirar - sensação de tontura ou desmaio - sudorese - náusea - vômito - batimentos cardíacos rápidos ou irregulares - falta de ar - sonolência incomum - fraqueza repentina - confusão ou dificuldade em pensar - dor de c...
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
Para pessoas com pressão alta, o objetivo do tratamento é reduzir a pressão arterial e reduzir o risco de doenças cardíacas, acidente vascular cerebral, insuficiência renal e outras complicações da doença. 
                
A pressão arterial normal é uma pressão arterial de 120/80 mmHg. A pressão arterial elevada é uma pressão arterial superior a 140/90 mmHg.
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
A diabetes tipo 2 pode ser controlada com um plano de tratamento que inclui mudanças no estilo de vida e medicamentos. O seu médico poderá recomendar um ou mais dos seguintes:
                
- mudanças no estilo de vida - medicamentos para diabetes - outros medicamentos - cirurgia para perda de peso - transplante de células de córtex renal
                
Mudanças no estilo de vida
                
Mudanças no estilo de vida, como perda de peso e atividade física, podem melhorar o controle da...
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
Quais são os efeitos colaterais da metformina? A maioria das pessoas tolera bem a metformina, mas alguns podem sentir efeitos colaterais. Os efeitos colaterais mais comuns da metformina incluem: - diarreia - dor abdominal - gases - náuseas e vômitos - dor de cabeça - inchaço dos pés e tornozelos - cansaço A diarreia é o efeito colateral mais comum. Os efeitos colaterais podem ser reduzidos esvaziando a bexiga completamente e bebendo muita água. A diarreia geralmente desaparece com o tempo. A met...
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
As contraindicações à aspirina incluem alergia à aspirina, doença renal, doença hepática, doença cardíaca, doença da válvula cardíaca, doença arterial periférica, doença arterial cerebral, insuficiência cardíaca, glaucoma, hemorragia interna ou externa, hipertensão, alta idade, doença reumática, doença de Reye, doença de Addison, doença de Crohn, doença de Peutz-Jeghers, doença de Whipple, doença de Hodgkin, doença de Hodgkin, doença de Hodgkin, doença de Hodgkin, doença de Hodgkin, doença de Ho...
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
Não existe tratamento para prevenir o diabetes tipo 2, mas você pode tomar medidas para reduzir os riscos de desenvolver a doença.
                
Se você tem diabetes, pode prevenir ou retardar problemas relacionados ao diabetes, como doenças cardíacas, doenças renais e problemas oculares. Isso pode ajudá-lo a viver mais tempo e melhor.
                
Pontos-chave
                
- Você pode prevenir ou retardar o diabetes tipo 2 com mudanças no estilo de vida. - Se você tem diabetes, pode ...
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
As medidas de prevenção da doença cardíaca incluem mudanças no estilo de vida, medicamentos e procedimentos médicos.
                
Mudanças no Estilo de Vida
                
Mudanças no estilo de vida são uma das melhores maneiras de prevenir doenças cardíacas. Algumas mudanças que você pode fazer são:
                
Fazer mais exercícios. Exercícios regularmente pode reduzir a pressão arterial, o nível de colesterol no sangue e o peso. Além disso, os exercícios podem melhorar seu nível de...
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
- Um acidente vascular cerebral (AVC) ocorre quando o fluxo sanguíneo para o cérebro é interrompido ou bloqueado.  - O AVC é um problema médico grave que requer tratamento imediato.  - Uma pessoa que apresenta sintomas de AVC deve ligar para o 9-1-1 imediatamente para solicitar atendimento médico de emergência.  - Uma pessoa que acredita que alguém está tendo um AVC deve ligar para o 9-1-1 imediatamente.  - Pessoas que tiveram um AVC devem descobrir o tipo de AVC que tiveram.  - Pessoas que tive...
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
Uma parada cardiorrespiratória, também conhecida como parada cardiorrespiratória, é uma situação grave na qual o coração para de bater e a respiração parada. Uma parada cardiorrespiratória pode ser fatal se não for tratada imediatamente.
                
Para ajudar alguém que está tendo um ataque cardíaco ou parada cardiorrespiratória, você deve chamar imediatamente para o 9-1-1.
                
Uma pessoa que não está respirando ou não tem pulso pode estar em parada cardiorrespiratória.
     ...
```

</details>
