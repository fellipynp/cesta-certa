class ErroRegra(Exception):
    """Erro de regra de negócio, com o status HTTP que deve ser devolvido."""

    def __init__(self, status: int, mensagem: str):
        super().__init__(mensagem)
        self.status = status
        self.mensagem = mensagem
