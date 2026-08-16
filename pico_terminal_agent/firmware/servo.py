"""Driver PWM conservador para microservos posicionais no GP15."""

from machine import Pin, PWM


class Servo:
    """Controla um servo posicional com pulsos de 1.000 a 2.000 us."""

    def __init__(self, pin=15, min_us=1000, max_us=2000, frequency=50):
        self._min_us = min_us
        self._max_us = max_us
        self._period_us = 1000000 // frequency
        self._pwm = PWM(Pin(pin))
        self._pwm.freq(frequency)
        self._angle = 90
        self.release()

    def write(self, angle):
        angle = max(0, min(180, int(angle)))
        pulse_us = self._min_us + (
            (self._max_us - self._min_us) * angle // 180
        )
        duty = pulse_us * 65535 // self._period_us
        self._pwm.duty_u16(duty)
        self._angle = angle

    def read(self):
        """Retorna o último ângulo comandado; servos comuns não têm feedback."""
        return self._angle

    def release(self):
        """Interrompe os pulsos para reduzir consumo e aquecimento após o gesto."""
        self._pwm.duty_u16(0)

