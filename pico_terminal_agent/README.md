# Agente TinyML de terminal para Raspberry Pi Pico

Este projeto executa na própria Raspberry Pi Pico um agente pequeno e restrito ao
domínio de conversa básica, controle do LED e um servo posicional. O computador conectado por USB é
apenas o teclado e a tela; a classificação, memória, planejamento e execução
ficam na placa.

Ele **não é um LLM** e não gera respostas livres. Em vez disso, combina:

- classificador de intenções treinado e quantizado em `int8`;
- memória curta da conversa;
- crenças sobre o estado físico do LED e a posição comandada do servo;
- objetivos e planejamento de ações;
- ferramentas para observar, acender, apagar e piscar o LED, além de mover o servo;
- verificação do resultado e uma segunda tentativa quando necessário.

## Teste primeiro no computador

Não há dependências externas. No PowerShell, execute:

```powershell
cd C:\FONTES\Estudos\Estudo_Python\pico_terminal_agent
python demo_pc.py
```

Exemplo de conversa:

```text
Você> olá
Pico(simulada)> Olá! Eu sou o pequeno agente desta Pico.

Você> por gentileza acenda a luz
      [LED ACESO]
Pico(simulada)> Sim. Planejei e executei 3 ações; LED aceso.

Você> a luz está acesa?
Pico(simulada)> Sim, o LED está aceso.

Você> pisque duas vezes
      [LED APAGADO]
      [LED ACESO]
      [LED APAGADO]
      [LED ACESO]
      [LED APAGADO]
      [LED ACESO]
Pico(simulada)> Objetivo concluído: 2 piscadas, 12 ações e estado original restaurado.

Você> acene duas vezes
      [SERVO 90°]
      [SERVO 60°]
      [SERVO 120°]
      [SERVO 60°]
      [SERVO 120°]
      [SERVO 90°]
      [SERVO LIVRE]
Pico(simulada)> Aceno concluído: 2 movimentos, 14 ações e servo centralizado.
```

## Ligação do servo

O driver usa um servo **posicional** no `GP15` (pino físico 20):

```text
Pico GP15 ───────── sinal do servo (amarelo/laranja)

Fonte 5 V (+) ───── alimentação do servo (vermelho)

Fonte 5 V (-) ─┬── terra do servo (marrom/preto)
                └── GND da Pico
```

Não alimente o servo pelo pino `3V3`. Use uma fonte externa adequada e mantenha
o GND da fonte, do servo e da Pico em comum. A Pico pode continuar alimentada
pelo USB. O gesto usa uma faixa conservadora de 60° a 120°, retorna a 90° e
interrompe os pulsos ao terminar. Esse código não serve para servo de rotação
contínua.

## Instalação na Pico

1. Instale uma versão atual do MicroPython para sua placa:
   [Pico](https://micropython.org/download/RPI_PICO/) ou
   [Pico W](https://micropython.org/download/RPI_PICO_W/).
2. No Thonny, selecione o interpretador **MicroPython (Raspberry Pi Pico)**.
3. Copie estes sete arquivos da pasta `firmware` para a raiz da placa:
   - `main.py`
   - `agent.py`
   - `classifier.py`
   - `model_data.py`
   - `text_processing.py`
   - `tools.py`
   - `servo.py`
4. Reinicie a placa ou pressione `Ctrl+D` no Shell do Thonny.
5. Escreva as mensagens quando aparecer `Você>`.

O Shell do Thonny já funciona como terminal USB. Para usar PuTTY ou outro
terminal serial, feche o Thonny, abra a porta `COM` da Pico e use `115200 baud`.
Somente um programa pode manter a porta aberta por vez.

## Frases que o modelo reconhece

O modelo possui 15 intenções, incluindo:

- saudação, identidade, capacidades, ajuda e agradecimento;
- despedida;
- acender, apagar e piscar o LED;
- acenar uma quantidade configurável de vezes com o servo;
- consultar o estado geral do LED;
- responder se o LED está aceso ou apagado;
- recuperar a última mensagem da memória;
- recusar pedidos fora do domínio.

Experimente variações naturais. O classificador não procura uma palavra com uma
cadeia de `if`: ele pontua unigramas e bigramas usando pesos aprendidos. Por ser
um modelo muito pequeno, algumas formulações novas poderão ser classificadas
incorretamente. Nesses casos, acrescente exemplos ao conjunto de treinamento.

## Retreinar o modelo

Edite `training/dataset.py` e execute:

```powershell
python training\train.py
python -m unittest discover -s tests -v
```

O treinamento usa somente a biblioteca padrão do Python. Ele sobrescreve
`firmware/model_data.py` com os pesos quantizados. Depois, copie novamente esse
arquivo para a Pico.

O modelo contém cerca de 7,6 KB de pesos `int8`. O arquivo exportado usa
um literal binário para não criar milhares de inteiros temporários no heap do
MicroPython durante a inicialização.

## Estrutura

```text
pico_terminal_agent/
├── demo_pc.py                 # conversa simulada no computador
├── firmware/
│   ├── main.py                # terminal USB
│   ├── agent.py               # memória, objetivos, plano e execução
│   ├── classifier.py          # inferência TinyML
│   ├── model_data.py          # pesos int8 gerados
│   ├── text_processing.py     # normalização e atributos
│   ├── servo.py               # PWM conservador no GP15
│   └── tools.py               # LED, servo e temporização da Pico
├── training/
│   ├── dataset.py             # frases rotuladas
│   └── train.py               # treinamento e exportação
└── tests/
    └── test_agent.py
```

## Limites desta primeira versão

- A memória dura somente até a placa reiniciar.
- O agente conversa apenas dentro das intenções treinadas.
- Não há acesso à internet nem geração de linguagem.
- LED e servo são os únicos atuadores, portanto o ambiente ainda é pequeno.

Mesmo com esses limites, há separação real entre percepção, modelo aprendido,
estado interno, objetivo, planejamento, ferramentas e avaliação do resultado.
