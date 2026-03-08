# Comparação: Modelo Base vs Fine-Tuned

**Data:** 2026-03-08 15:01

## Métricas Agregadas

### Sobreposição entre modelos (FT vs Baseline)

| Métrica | Valor |
|---------|-------|
| Comprimento médio (Base) | 1225 chars |
| Comprimento médio (Fine-tuned) | 1230 chars |
| Ratio de comprimento (FT/Base) | 1.06x |
| BLEU Score | 0.0312 |
| ROUGE-1 F1 | 0.3007 |
| ROUGE-2 F1 | 0.0793 |
| ROUGE-L F1 | 0.1704 |

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
Os sintomas do diabetes tipo 2 podem incluir:
                
Sintomas de diabetes tipo 1 e tipo 2 podem ser semelhantes, mas o diabetes tipo 1 geralmente começa mais rapidamente.
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
O MI pode ser um evento fatal se não for tratado imediatamente. Converse com seu médico sobre o que fazer durante um MI. Eles podem ensinar-lhe a fazer um teste de triagem de MI, chamado DASI-2 (Teste de Avaliação do Infarto do Miocárdio), se você tiver um sintoma do MI. Você pode fazer o teste por conta própria se você tiver um sintoma e não estiver no hospital. O teste de triagem de MI pode ajudar você a descobrir se precisa de atendimento médico imediato.
                
Você pode usar o tes...
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
A hipertensão arterial é tratada com medicamentos e mudanças no estilo de vida. Muitos medicamentos são usados ​​para tratar a hipertensão arterial. A maioria deles controla a pressão arterial em um ou dois dos três sistemas. Muitos tratamentos são usados ​​em combinação.
                
Muitos medicamentos para pressão arterial podem ser usados ​​por pessoas com diabetes e/ou doença renal.
                
Os medicamentos para hipertensão arterial incluem:
                
Atenolol e metoprolo...
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
A maioria dos médicos recomenda que as pessoas com diabetes tipo 2 se esforcem para perder peso e aumente a atividade física. Muitas pessoas com diabetes tipo 2 também precisam tomar medicamentos.
                
Medicamentos
                
Pessoas com diabetes tipo 2 podem precisar tomar insulina e/ou medicamentos orais. Os medicamentos orais não funcionam tão bem para pessoas com excesso de peso ou obesidade.
                
A insulina é um medicamento que pessoas com diabetes tipo 1 e tip...
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
A metformina pode causar efeitos colaterais comuns e leves. Os efeitos colaterais mais comuns incluem diarreia, náuseas e vômitos. A maioria dos sintomas geralmente desaparece com o tempo. Se você tiver diarreia, você pode tomar a metformina depois de comer. Além disso, você pode tentar tomar um dosados mais baixo para começar. Você também pode tentar tomar metformina ao mesmo tempo com um inibidor do canal de sódio (ISS). ISSs incluem amilorid, triamterena e quinapril.
                
Os efeit...
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
As contraindicações para aspirina incluem histórico pessoal de:
                
Ataque cardíaco
                
Insuficiência cardíaca
                
Insuficiência renal
                
Insuficiência hepática
                
Hemorragia cerebral
                
Ulceras pépticas
                
Insuficiência respiratória
                
Ataque isquêmico transitório
                
Doença de Crohn
                
Doença de Behçet
                
Osteoporose
                
Ataque alérg...
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
Não é possível prevenir o diabetes tipo 2, mas você pode atrasar ou prevenir a doença em um estágio precoce. A prevenção é especialmente importante para pessoas que tenham histórico familiar da doença, que tenham um peso elevado ou que tenham outras condições de saúde que aumentem o risco de diabetes tipo 2.
                
Se você tem diabetes tipo 2, pode atrasar ou prevenir a complicação do diabetes com um estilo de vida saudável. Isso inclui um bom controle do peso, exercícios regulares e u...
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
Muitas pessoas com doenças cardíacas podem reduzir o risco de eventos cardiovasculares futuros com um programa de manejo do risco. Uma pessoa deve ter um histórico médico completo, um exame físico completo e um avaliamento de risco cardiovascular. O objetivo do manejo do risco é reduzir o risco de eventos cardiovasculares como ataque cardíaco, acidente vascular cerebral e insuficiência cardíaca. Uma pessoa deve ter um histórico médico completo, um exame físico completo e um avaliamento de risco ...
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
- Um acidente vascular cerebral (AVC) ocorre quando o fluxo sanguíneo para o cérebro é interrompido por um coágulo sanguíneo, um bloqueio ou uma ruptura de uma artéria.  - O tratamento para AVC é mais eficaz quando for administrado na primeira hora após o início dos sintomas.  - Os sintomas de AVC incluem tonturas, dor de cabeça, dificuldade para fala, paralisia de um lado do corpo e visão dupla.  - O AVC é um problema de saúde muito grave.  - O tratamento para AVC inclui medicamentos e cirurgia...
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
Um agente de emergência deve ser chamado imediatamente. O agente de emergência chamado deve dar aos prestadores de cuidados de emergência o seguinte:
                
- Código de alerta - Local - Onde estão os prestadores de cuidados de emergência - O que ocorreu - O que ocorreu - O que ocorreu - O que pode acontecer - O que pode acontecer - O que pode acontecer - O que pode acontecer - O que pode acontecer - O que pode acontecer - O que pode acontecer - O que pode acontecer - O que pode acontec...
```

</details>
