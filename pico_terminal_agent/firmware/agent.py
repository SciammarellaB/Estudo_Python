"""Agente orientado a objetivos para conversa e controle do LED."""

from text_processing import normalize


_NUMBER_WORDS = {
    "um": 1,
    "uma": 1,
    "dois": 2,
    "duas": 2,
    "tres": 3,
    "quatro": 4,
    "cinco": 5,
}


class ConversationAgent:
    def __init__(self, classifier, tools):
        self.classifier = classifier
        self.tools = tools
        self.beliefs = {
            "led_on": bool(self.tools.read_led()),
            "servo_angle": int(self.tools.read_servo_angle()),
            "turn": 0,
            "last_intent": None,
        }
        self.current_goal = None
        self.memory = []

    def _remember(self, user_text, intent, answer):
        self.memory.append({
            "user": user_text,
            "intent": intent,
            "answer": answer,
        })
        if len(self.memory) > 8:
            self.memory.pop(0)

    def _sync_beliefs(self):
        self.beliefs["led_on"] = bool(self.tools.read_led())
        self.beliefs["servo_angle"] = int(self.tools.read_servo_angle())

    def _extract_count(self, text):
        for token in normalize(text).split():
            if token in _NUMBER_WORDS:
                return _NUMBER_WORDS[token]
            try:
                value = int(token)
                return max(1, min(5, value))
            except ValueError:
                pass
        return 3

    def _plan(self, goal):
        """Gera ações usando o estado atual, sem depender da frase original."""
        self._sync_beliefs()
        actions = []

        if goal["kind"] == "led_state":
            target = bool(goal["target"])
            if self.beliefs["led_on"] != target:
                actions.append(("set_led", target))
                actions.append(("wait", 50))
            actions.append(("verify_led", target))
            return actions

        if goal["kind"] == "blink":
            count = goal["count"]
            final_state = bool(goal["final_state"])

            if self.beliefs["led_on"]:
                actions.append(("set_led", False))
                actions.append(("wait", 150))

            for _ in range(count):
                actions.append(("set_led", True))
                actions.append(("wait", 220))
                actions.append(("set_led", False))
                actions.append(("wait", 180))

            if final_state:
                actions.append(("set_led", True))
            actions.append(("verify_led", final_state))
            return actions

        if goal["kind"] == "wave":
            count = goal["count"]
            actions.append(("servo_angle", 90))
            actions.append(("wait", 400))

            for _ in range(count):
                actions.append(("servo_angle", 60))
                actions.append(("wait", 350))
                actions.append(("servo_angle", 120))
                actions.append(("wait", 350))

            actions.append(("servo_angle", 90))
            actions.append(("wait", 400))
            actions.append(("verify_servo", 90))
            actions.append(("release_servo", True))
            return actions

        return actions

    def _execute_plan(self, actions):
        for action, value in actions:
            if action == "set_led":
                self.tools.set_led(value)
                self.beliefs["led_on"] = bool(value)
            elif action == "wait":
                self.tools.wait_ms(value)
            elif action == "verify_led":
                self._sync_beliefs()
                if self.beliefs["led_on"] != bool(value):
                    return False
            elif action == "servo_angle":
                self.tools.set_servo_angle(value)
                self.beliefs["servo_angle"] = int(value)
            elif action == "verify_servo":
                self._sync_beliefs()
                if self.beliefs["servo_angle"] != int(value):
                    return False
            elif action == "release_servo":
                self.tools.release_servo()
        return True

    def _achieve(self, goal):
        self.current_goal = goal
        plan = self._plan(goal)
        success = self._execute_plan(plan)

        # Para metas de estado, uma falha causa uma nova observação e tentativa.
        if not success and goal["kind"] == "led_state":
            success = self._execute_plan(self._plan(goal))

        self.current_goal = None
        self._sync_beliefs()
        return success, len(plan)

    def _answer_for_intent(self, intent, text):
        if intent == "saudacao":
            return "Olá! Eu sou o pequeno agente desta Pico.", False

        if intent == "identidade":
            return (
                "Sou um agente TinyML local: classifico intenções, mantenho "
                "memória, crio objetivos e uso ferramentas da Pico.",
                False,
            )

        if intent == "capacidades":
            return (
                "Consigo conversar dentro do meu domínio, lembrar mensagens, "
                "consultar, acender, apagar e piscar o LED, além de acenar "
                "com um servo no GP15.",
                False,
            )

        if intent == "ajuda":
            return (
                "Tente: 'quem é você?', 'acenda o LED', 'pisque duas vezes', "
                "'acene para mim', 'o LED está apagado?' ou "
                "'o que eu disse antes?'.",
                False,
            )

        if intent == "agradecimento":
            return "Por nada. Objetivo cumprido!", False

        if intent == "despedida":
            return "Até logo. Vou encerrar a conversa.", True

        if intent == "memoria":
            if not self.memory:
                return "Ainda não tenho uma mensagem anterior na memória.", False
            return "Sua última mensagem foi: " + repr(self.memory[-1]["user"]), False

        if intent == "estado_led":
            self._sync_beliefs()
            state = "aceso" if self.beliefs["led_on"] else "apagado"
            return "O LED está " + state + ".", False

        if intent == "consulta_aceso":
            self._sync_beliefs()
            if self.beliefs["led_on"]:
                return "Sim, o LED está aceso.", False
            return "Não, o LED está apagado.", False

        if intent == "consulta_apagado":
            self._sync_beliefs()
            if not self.beliefs["led_on"]:
                return "Sim, o LED está apagado.", False
            return "Não, o LED está aceso.", False

        if intent == "ligar_led":
            already_on = bool(self.tools.read_led())
            success, action_count = self._achieve({
                "kind": "led_state",
                "target": True,
            })
            if not success:
                return "Não consegui confirmar que o LED acendeu.", False
            if already_on:
                return "Sim. O LED já estava aceso.", False
            return "Sim. Planejei e executei " + str(action_count) + " ações; LED aceso.", False

        if intent == "desligar_led":
            already_off = not bool(self.tools.read_led())
            success, action_count = self._achieve({
                "kind": "led_state",
                "target": False,
            })
            if not success:
                return "Não consegui confirmar que o LED apagou.", False
            if already_off:
                return "Sim. O LED já estava apagado.", False
            return "Sim. Planejei e executei " + str(action_count) + " ações; LED apagado.", False

        if intent == "piscar_led":
            count = self._extract_count(text)
            self._sync_beliefs()
            final_state = self.beliefs["led_on"]
            success, action_count = self._achieve({
                "kind": "blink",
                "count": count,
                "final_state": final_state,
            })
            if not success:
                return "Executei o plano, mas o estado final não foi confirmado.", False
            return (
                "Objetivo concluído: " + str(count) + " piscadas, "
                + str(action_count) + " ações e estado original restaurado.",
                False,
            )

        if intent == "acenar_servo":
            count = self._extract_count(text)
            success, action_count = self._achieve({
                "kind": "wave",
                "count": count,
            })
            if not success:
                return "Executei o aceno, mas não confirmei a posição central.", False
            return (
                "Aceno concluído: " + str(count) + " movimentos, "
                + str(action_count) + " ações e servo centralizado.",
                False,
            )

        return (
            "Não compreendi com segurança. Meu domínio é conversa básica, LED "
            "e acenos com o servo; peça ajuda para ver exemplos.",
            False,
        )

    def handle(self, text):
        text = text.strip()
        if not text:
            return {
                "text": "Digite alguma mensagem.",
                "exit": False,
                "intent": "desconhecido",
                "margin": 0,
            }

        prediction = self.classifier.predict(text)
        intent = prediction["intent"]
        answer, should_exit = self._answer_for_intent(intent, text)

        self.beliefs["turn"] += 1
        self.beliefs["last_intent"] = intent
        self._remember(text, intent, answer)

        return {
            "text": answer,
            "exit": should_exit,
            "intent": intent,
            "margin": prediction["margin"],
        }
