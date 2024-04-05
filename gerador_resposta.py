# --- Importar as bibliotecas --- #
from time import sleep
from random import choice


def gerador_resposta() -> str:
    """
    Função responsável por gerar a resposta do bot.
    :return: String com a resposta do bot.
    """
    # --- Lista com as respostas --- #
    respostas = [
        'Olá, bioinformata! Como posso ajudá-lo?',
        'Você precisa de alguma ajuda?',
        'Digite algo no prompt que eu te ajudarei!'
    ]

    # --- Escolher uma resposta --- #
    resposta = choice(respostas)

    # --- Armazenar a resposta e escrevê-la de modo pausado --- #
    for palavra in resposta.split():
        yield palavra + ' '
        sleep(0.05)
