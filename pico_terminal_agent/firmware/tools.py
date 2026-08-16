"""Ferramentas físicas que o agente pode selecionar durante um plano."""

from machine import Pin
import time

from servo import Servo


SERVO_PIN = 15


class PicoTools:
    def __init__(self):
        # O alias LED funciona nas versões atuais do MicroPython para Pico e Pico W.
        self._led = Pin("LED", Pin.OUT)
        self._led.off()
        # Inicialização preguiçosa: o servo não se move durante o boot.
        self._servo = None
        self._servo_angle = 90

    def _get_servo(self):
        if self._servo is None:
            self._servo = Servo(SERVO_PIN)
        return self._servo

    def set_led(self, enabled):
        self._led.value(1 if enabled else 0)

    def read_led(self):
        return bool(self._led.value())

    def wait_ms(self, duration):
        time.sleep_ms(duration)

    def set_servo_angle(self, angle):
        angle = max(0, min(180, int(angle)))
        self._get_servo().write(angle)
        self._servo_angle = angle

    def read_servo_angle(self):
        return self._servo_angle

    def release_servo(self):
        if self._servo is not None:
            self._servo.release()
