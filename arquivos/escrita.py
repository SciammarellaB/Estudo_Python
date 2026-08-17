import os
pasta = "arquivos/dados/"
caminho = "arquivos/dados/nomes.txt"

os.makedirs(pasta, exist_ok=True)

with open(caminho, "a", encoding="utf-8"):
    pass

nome = input("Digite seu nome: \n")

if nome.strip() == "":  # Verifica se o nome não está vazio
    raise ValueError("O nome não pode estar vazio. Por favor, insira um nome válido.")

arquivo = open(f"{caminho}", "r", encoding="utf-8")

file = open(f"{caminho}", "a", encoding="utf-8")
file.write(f"{nome}\n")
file.close()

nomes = []

with open(f"{caminho}", "r", encoding="utf-8") as file:
    for line in file:
        nomes.append(line.rstrip())

for nome in sorted(nomes):
    print(f"Olá: {nome}")