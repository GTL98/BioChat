# --- Importar as bibliotecas --- #
from time import sleep
from chat import BioChat


def gerador_resposta(prompt: str) -> str:
    """
    Função responsável por gerar a resposta do bot.
    :param prompt: Entrada do usuário.
    :return: String com a resposta do bot.
    """
    # --- Inicializar a classe --- #
    chat = BioChat(prompt)

    # --- Criar a resposta --- #
    resposta = chat.criar_reposta()

    # --- Armazenar a resposta e escrevê-la de modo pausado --- #
    for palavra in resposta.split():
        yield palavra + ' '
        sleep(0.05)
