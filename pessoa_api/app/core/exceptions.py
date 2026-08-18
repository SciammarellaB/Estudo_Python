class ApplicationError(Exception):
    """Erro esperado da aplicação, independente do protocolo HTTP."""


class PessoaNaoEncontradaError(ApplicationError):
    def __init__(self) -> None:
        super().__init__("Pessoa não encontrada.")


class EmailJaCadastradoError(ApplicationError):
    def __init__(self) -> None:
        super().__init__("Já existe uma pessoa cadastrada com esse e-mail.")
