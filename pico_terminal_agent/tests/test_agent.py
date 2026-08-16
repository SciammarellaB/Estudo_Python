"""Testes no computador, sem precisar conectar a Pico."""

from pathlib import Path
import sys
import unittest


PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR / "firmware"))

from agent import ConversationAgent  # noqa: E402
from classifier import TinyIntentClassifier  # noqa: E402


class FakeTools:
    def __init__(self):
        self.led_on = False
        self.waits = []
        self.servo_angle = 90
        self.servo_released = True
        self.servo_commands = []

    def set_led(self, enabled):
        self.led_on = bool(enabled)

    def read_led(self):
        return self.led_on

    def wait_ms(self, duration):
        self.waits.append(duration)

    def set_servo_angle(self, angle):
        self.servo_angle = int(angle)
        self.servo_released = False
        self.servo_commands.append(self.servo_angle)

    def read_servo_angle(self):
        return self.servo_angle

    def release_servo(self):
        self.servo_released = True


class AgentTests(unittest.TestCase):
    def setUp(self):
        self.tools = FakeTools()
        self.agent = ConversationAgent(TinyIntentClassifier(), self.tools)

    def ask(self, text):
        return self.agent.handle(text)

    def test_basic_conversation(self):
        self.assertEqual(self.ask("Olá, Pico")["intent"], "saudacao")
        self.assertEqual(self.ask("Quem é você?")["intent"], "identidade")
        self.assertEqual(
            self.ask("Quais ferramentas você possui?")["intent"],
            "capacidades",
        )

    def test_agent_plans_led_goal_and_answers_yes_no(self):
        result = self.ask("Por favor, ilumine isso")
        self.assertEqual(result["intent"], "ligar_led")
        self.assertTrue(self.tools.led_on)

        result = self.ask("O LED está aceso?")
        self.assertEqual(result["intent"], "consulta_aceso")
        self.assertTrue(result["text"].startswith("Sim"))

        result = self.ask("Desative a luz")
        self.assertEqual(result["intent"], "desligar_led")
        self.assertFalse(self.tools.led_on)

        result = self.ask("O LED está apagado?")
        self.assertEqual(result["intent"], "consulta_apagado")
        self.assertTrue(result["text"].startswith("Sim"))

    def test_blink_restores_previous_state(self):
        self.tools.led_on = True
        result = self.ask("Pisca duas vezes")
        self.assertEqual(result["intent"], "piscar_led")
        self.assertTrue(self.tools.led_on)
        self.assertIn("2 piscadas", result["text"])

    def test_short_term_memory(self):
        self.ask("Bom dia")
        result = self.ask("Você lembra do que falei?")
        self.assertEqual(result["intent"], "memoria")
        self.assertIn("Bom dia", result["text"])

    def test_agent_plans_servo_wave_and_returns_to_center(self):
        result = self.ask("Acene duas vezes para mim")
        self.assertEqual(result["intent"], "acenar_servo")
        self.assertEqual(self.tools.servo_commands, [90, 60, 120, 60, 120, 90])
        self.assertEqual(self.tools.servo_angle, 90)
        self.assertTrue(self.tools.servo_released)
        self.assertIn("2 movimentos", result["text"])

    def test_unknown_request_is_refused(self):
        result = self.ask("Faça café para mim")
        self.assertEqual(result["intent"], "desconhecido")
        self.assertFalse(self.tools.led_on)

    def test_classifier_generalizes_to_unseen_phrases(self):
        samples = (
            ("Oi, tudo certo?", "saudacao"),
            ("Qual o seu nome?", "identidade"),
            ("Me explique suas habilidades", "capacidades"),
            ("Por gentileza, acenda a luz", "ligar_led"),
            ("A luz segue acesa?", "consulta_aceso"),
            ("Me conte a situação do LED", "estado_led"),
            ("Dê um sinal piscando", "piscar_led"),
            ("Pode cumprimentar usando o braço?", "acenar_servo"),
            ("Recorda minha última fala?", "memoria"),
            ("Obrigado pela ajuda", "agradecimento"),
            ("Até a próxima", "despedida"),
            ("Qual a cor do céu?", "desconhecido"),
        )

        classifier = TinyIntentClassifier()
        for phrase, expected in samples:
            with self.subTest(phrase=phrase):
                self.assertEqual(classifier.predict(phrase)["intent"], expected)


if __name__ == "__main__":
    unittest.main()
