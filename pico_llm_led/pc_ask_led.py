import argparse
import json
import sys
import time
import urllib.error
import urllib.request


def require_serial():
    try:
        import serial
        from serial.tools import list_ports
    except ImportError:
        print("Instale a dependencia: python -m pip install pyserial", file=sys.stderr)
        raise SystemExit(2)
    return serial, list_ports


def list_serial_ports():
    _, list_ports = require_serial()
    ports = list(list_ports.comports())
    if not ports:
        print("Nenhuma porta serial encontrada.")
        return

    for port in ports:
        description = port.description or ""
        hwid = port.hwid or ""
        print(f"{port.device}\t{description}\t{hwid}")


def ask_ollama(question, model, host):
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Responda usando exatamente uma palavra: SIM ou NAO. "
                    "Nao explique. Nao use pontuacao. Se a pergunta nao puder "
                    "ser respondida como sim ou nao, escolha NAO."
                ),
            },
            {"role": "user", "content": question},
        ],
        "stream": False,
        "think": False,
        "options": {
            "temperature": 0,
            "num_predict": 32,
        },
    }

    request = urllib.request.Request(
        f"{host.rstrip('/')}/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        print(f"Falha ao chamar Ollama em {host}: {exc}", file=sys.stderr)
        print("Verifique se o Ollama esta aberto e se o modelo foi baixado.", file=sys.stderr)
        raise SystemExit(1)

    message = data.get("message") or {}
    raw_answer = str(message.get("content", "")).strip().upper()
    if raw_answer.startswith("SIM"):
        return "SIM", raw_answer
    if raw_answer.startswith("NAO") or raw_answer.startswith("NÃO"):
        return "NAO", raw_answer

    return "NAO", raw_answer


def send_to_pico(port, answer, baudrate):
    serial, _ = require_serial()
    command = "Y\n" if answer == "SIM" else "N\n"

    try:
        with serial.Serial(port, baudrate=baudrate, timeout=2) as pico:
            time.sleep(1.2)
            pico.write(command.encode("ascii"))
            pico.flush()
    except serial.SerialException as exc:
        print(f"Nao consegui abrir a porta {port}: {exc}", file=sys.stderr)
        print("Feche Thonny, PuTTY, Arduino IDE, monitor serial ou outro programa usando a Pico.", file=sys.stderr)
        print("Depois desconecte e conecte a Pico de novo, e confira a porta com --list-ports.", file=sys.stderr)
        raise SystemExit(1)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Pergunta a uma LLM local e envia SIM/NAO para o LED da Raspberry Pi Pico."
    )
    parser.add_argument("--list-ports", action="store_true", help="lista portas seriais")
    parser.add_argument("--port", help="porta serial da Pico, por exemplo COM5")
    parser.add_argument("--question", "-q", help="pergunta de sim ou nao")
    parser.add_argument("--model", default="tinyllama", help="modelo do Ollama")
    parser.add_argument("--host", default="http://localhost:11434", help="URL do Ollama")
    parser.add_argument("--baudrate", type=int, default=115200, help="baudrate da serial")
    parser.add_argument("--dry-run", action="store_true", help="consulta a LLM sem enviar comando para a Pico")
    return parser.parse_args()


def main():
    args = parse_args()

    if args.list_ports:
        list_serial_ports()
        return

    if not args.port:
        print("Informe a porta com --port COMx. Use --list-ports para descobrir.", file=sys.stderr)
        raise SystemExit(2)

    question = args.question
    if not question:
        question = input("Pergunta de sim/nao: ").strip()

    if not question:
        print("Pergunta vazia.", file=sys.stderr)
        raise SystemExit(2)

    answer, raw_answer = ask_ollama(question, args.model, args.host)
    print(f"LLM: {raw_answer or '(vazio)'}")
    print(f"Normalizado: {answer}")

    if args.dry_run:
        print("Dry-run: nenhum comando foi enviado para a Pico.")
        return

    send_to_pico(args.port, answer, args.baudrate)
    print("Comando enviado para a Pico.")


if __name__ == "__main__":
    main()
