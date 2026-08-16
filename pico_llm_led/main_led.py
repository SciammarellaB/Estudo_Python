from machine import Pin
from time import sleep
import sys


try:
    led = Pin("LED", Pin.OUT)
except TypeError:
    led = Pin(25, Pin.OUT)


def show_yes():
    blink(1)


def show_no():
    blink(2)


def blink(times):
    for _ in range(times):
        led.on()
        sleep(0.25)
        led.off()
        sleep(0.25)


def show_unknown():
    for _ in range(8):
        led.toggle()
        sleep(0.07)
    led.off()


led.off()

while True:
    line = sys.stdin.readline()
    if not line:
        sleep(0.05)
        continue

    command = line.strip().upper()

    if command in ("Y", "YES", "SIM", "S", "1"):
        show_yes()
    elif command in ("N", "NO", "NAO", "NÃO", "0"):
        show_no()
    else:
        show_unknown()
