# Pico LED Sim/Nao

Experimento simples para fazer perguntas de sim/nao e mostrar a resposta no LED da Raspberry Pi Pico.

Existem dois modos:

- `main_oraculo.py`: roda so na Pico e decide `SIM` ou `NAO` com uma regra boba baseada no texto.
- `main.py` + `pc_ask_led.py`: roda uma LLM no computador e envia `SIM` ou `NAO` para a Pico.

Comportamento do LED:

- `SIM`: LED pisca 1 vez.
- `NAO`: LED pisca 2 vezes.

## Modo mais simples: oraculo na Pico

Este e o melhor ponto de partida para brincar sem instalar nada no PC alem do Thonny.

1. Instale o MicroPython na Pico.
2. Abra o Thonny.
3. Copie o conteudo de `main_oraculo.py`.
4. Salve na Pico como `main.py`.
5. Abra o Shell/REPL do Thonny.
6. Digite uma pergunta de sim/nao e aperte Enter.

Exemplo:

```text
Oraculo Pico pronto. Digite uma pergunta de sim/nao e aperte Enter.
SIM = 1 piscada. NAO = 2 piscadas.
A Pico vai dominar o mundo?
NAO
```

Ele nao entende a pergunta de verdade. Ele transforma o texto em um numero e usa isso para escolher `SIM` ou `NAO`. Para um brinquedo com LED, isso ja e suficiente.

## Modo com LLM no PC

Fluxo:

```text
Pergunta no PC -> LLM local no PC -> resposta SIM/NAO -> USB serial -> LED da Pico
```

### 1. Gravar o programa na Pico

1. Instale o MicroPython na Pico.
2. Abra o Thonny.
3. Copie o conteudo de `main.py`.
4. Salve na Pico como `main.py`.
5. Reinicie a Pico.

Depois disso, feche o Thonny antes de rodar o script do PC, porque a porta serial USB não pode ser usada por dois programas ao mesmo tempo.

### 2. Preparar o PC

Instale a dependência serial:

```powershell
python -m pip install pyserial
```

Para usar uma LLM local, instale o Ollama e baixe um modelo pequeno:

```powershell
ollama pull tinyllama
```

### 3. Descobrir a porta da Pico

Liste as portas:

```powershell
python .\pico_llm_led\pc_ask_led.py --list-ports
```

Use a porta que aparecer como USB Serial, Pico, Board CDC ou similar.

### 4. Fazer uma pergunta

Exemplo:

```powershell
python .\pico_llm_led\pc_ask_led.py --port COM5 --question "Python e uma linguagem de programacao?"
```

Com outro modelo do Ollama:

```powershell
python .\pico_llm_led\pc_ask_led.py --port COM5 --model llama3.2:1b --question "A lua e maior que a Terra?"
```

Se a LLM responder `SIM`, a Pico acende o LED. Se responder `NAO`, a Pico pisca.
