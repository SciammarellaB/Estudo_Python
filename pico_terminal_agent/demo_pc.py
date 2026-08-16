"""Demonstra o mesmo agente no computador antes de copiar para a Pico."""

from pathlib import Path
import sys
import time


PROJECT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_DIR / "firmware"))

from agent import ConversationAgent  # noqa: E402
from classifier import TinyIntentClassifier  # noqa: E402


class SimulatedTools:
    def __init__(self):
        self._led_on = False
        self._servo_angle = 90

    def set_led(self, enabled):
        self._led_on = bool(enabled)
        print("      [LED {}]".format("ACESO" if self._led_on else "APAGADO"))

    def read_led(self):
        return self._led_on

    def wait_ms(self, duration):
        time.sleep(duration / 1000)

    def set_servo_angle(self, angle):
        self._servo_angle = int(angle)
        print("      [SERVO {}°]".format(self._servo_angle))

    def read_servo_angle(self):
        return self._servo_angle

    def release_servo(self):
        print("      [SERVO LIVRE]")


def main():
    agent = ConversationAgent(TinyIntentClassifier(), SimulatedTools())
    print("Pico(simulada)> Agente iniciado. Digite 'ajuda' ou Ctrl+C.")

    while True:
        try:
            result = agent.handle(input("\nVocê> "))
            print("Pico(simulada)>", result["text"])
            if result["exit"]:
                break
        except (KeyboardInterrupt, EOFError):
            print("\nPico(simulada)> Conversa encerrada.")
            break


if __name__ == "__main__":
    main()
