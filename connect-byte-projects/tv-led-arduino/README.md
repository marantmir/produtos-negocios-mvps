# Projeto de Março – Televisão com Arduino

Projeto mensal da Connect Byte.  
Neste mês será construída uma “televisão” utilizando LED simples ou LED RGB, botão e Arduino Uno, explorando conceitos fundamentais de eletrônica e programação embarcada.

---

## Objetivos do Projeto

O participante aprenderá:

- Conceitos básicos de eletrônica.
- Funcionamento e utilização de LEDs simples e LEDs RGB.
- Uso de resistores para limitação de corrente.
- Funcionamento de botões no Arduino.
- Alimentação da placa com bateria.
- Noções básicas de programação no Arduino IDE.
- Processo de upload de código para a placa.

---

## Componentes Utilizados

- Arduino Uno (necessário para LED RGB).
- LED simples.
- LED RGB.
- Resistores (220 Ω ou 330 Ω recomendados).
- Botão.
- Suporte de pilhas.
- Fios de conexão.
- Ferro de solda e estanho (quando aplicável).

---

## Etapas do Projeto

1. Soldagem do LED RGB (opcional caso seja utilizado).
2. Teste do LED simples diretamente na bateria.
3. Conexão do botão ao Arduino.
4. Conexão da bateria ao Arduino.
5. Upload do software (arquivo final do projeto).

---

## O que Você Vai Aprender

- Diferença entre 5V e GND.
- Como ocorre a circulação de corrente elétrica.
- Por que resistores são essenciais.
- Como o Arduino controla componentes.
- Como carregar código na placa Arduino.

---

## Atenções Importantes

### Nunca conectar LED diretamente ao 5V do Arduino

LEDs são componentes sensíveis e não possuem limitação própria de corrente.  
Conectar um LED diretamente assim:

5V → LED → GND

pode causar:

- Queima do LED.
- Danos ao pino do Arduino.
- Danos permanentes à placa.

### Finalidade do resistor

O resistor funciona como limitador de corrente, mantendo o circuito seguro.

Ligação correta:

5V → Resistor → LED → GND  
ou  
Pino digital → Resistor → LED → GND

Valores recomendados:

- 220 Ω
- 330 Ω

---

## Verificação de Polaridade

### LED Simples

- Perna maior: ânodo (positivo).  
- Perna menor: cátodo (negativo).  
- Base achatada: lado negativo.

Ligação:

Pino digital ou 5V → Resistor → Ânodo  
Cátodo → GND

### LED RGB

Possui quatro pernas.  
Uma delas é a perna comum:

- Cátodo comum → conectar ao GND.  
- Ânodo comum → conectar ao 5V.  

Verificar:

- Datasheet do modelo.
- Tamanho da perna.
- Teste com multímetro (modo diodo).

Cada cor deve possuir seu próprio resistor.

### Suporte de Bateria
![Descrição da imagem](/img/supor

- Fio vermelho: positivo.
- Fio preto: negativo.

No Arduino:

- VIN ou 5V → positivo.
- GND → negativo.

Inversão pode danificar a placa.

---

## Como Começar

1. Ler a Wiki completa do projeto.
2. Separar todos os materiais.
3. Realizar a montagem com calma.
4. Testar cada etapa individualmente.

---

## Suporte

Em caso de dúvidas, consulte a Wiki detalhada ou solicite auxílio no grupo Connect Byte.

---

Feito com 💙 para quem está começando no mundo da tecnologia.
Connect Byte • Março 2026