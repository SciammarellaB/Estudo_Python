"""Ponto de entrada do chat pelo terminal USB da Raspberry Pi Pico."""

from agent import ConversationAgent
from classifier import TinyIntentClassifier
from tools import PicoTools


DEBUG_CLASSIFIER = False


def run():
    agent = ConversationAgent(TinyIntentClassifier(), PicoTools())

    print()
    print("Pico> Agente TinyML iniciado.")
    print("Pico> Converse comigo ou escreva 'ajuda'. Ctrl+C encerra.")

    while True:
        try:
            message = input("\nVocê> ")
            result = agent.handle(message)
            print("Pico>", result["text"])

            if DEBUG_CLASSIFIER:
                print(
                    "[debug] intenção=",
                    result["intent"],
                    " margem=",
                    result["margin"],
                )

            if result["exit"]:
                break
        except KeyboardInterrupt:
            print("\nPico> Conversa encerrada.")
            break


run()

