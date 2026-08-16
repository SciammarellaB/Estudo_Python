from machine import Pin
from time import sleep
import sys


try:
    led = Pin("LED", Pin.OUT)
except TypeError:
    led = Pin(25, Pin.OUT)


def blink(times, on_time=0.22, off_time=0.22):
    for _ in range(times):
        led.on()
        sleep(on_time)
        led.off()
        sleep(off_time)


def answer_yes_no(question):
    score = 0
    for index, char in enumerate(question.lower(), start=1):
        score += index * ord(char)
    return "SIM" if score % 2 == 0 else "NAO"


def normalize_text(text):
    text = text.lower()
    text = text.replace("á", "a")
    text = text.replace("à", "a")
    text = text.replace("ã", "a")
    text = text.replace("â", "a")
    text = text.replace("é", "e")
    text = text.replace("ê", "e")
    text = text.replace("í", "i")
    text = text.replace("ó", "o")
    text = text.replace("õ", "o")
    text = text.replace("ô", "o")
    text = text.replace("ú", "u")
    text = text.replace("ç", "c")
    return text


def run_led_command(text):
    text = normalize_text(text)

    if "led" not in text and "luz" not in text:
        return False

    if "desliga" in text or "desligar" in text or "apaga" in text or "apagar" in text:
        led.off()
        print("LED DESLIGADO")
        return True

    if "liga" in text or "ligar" in text or "acende" in text or "acender" in text:
        led.on()
        print("LED LIGADO")
        return True

    return False


def show_answer(answer):
    if answer == "SIM":
        blink(1)
    else:
        blink(2)


led.off()
print("Oraculo Pico pronto. Digite uma pergunta de sim/nao e aperte Enter.")
print("SIM = 1 piscada. NAO = 2 piscadas.")
print("Comandos: ligar led, desligar led.")

while True:
    line = sys.stdin.readline()
    if not line:
        sleep(0.05)
        continue

    question = line.strip()
    if not question:
        continue

    if run_led_command(question):
        continue

    answer = answer_yes_no(question)
    print(answer)
    show_answer(answer)
