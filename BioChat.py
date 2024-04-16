# --- Importar as bibliotecas --- #
import streamlit as st
from gerador_resposta import gerador_resposta

# --- Configuração da página --- #
st.set_page_config(
    page_title='BioChat',
    layout='centered'
)

# --- Título à página --- #
st.title('BioChat :speech_balloon::dna:')

# --- Criar uma lista para armazenar o histórico do usuário --- #
if 'messages' not in st.session_state:
    st.session_state.messages = []
    
# --- Mostrar as messagens do chat a partir do histórico --- #
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])


# --- Entrada do usuário --- #
if prompt := st.chat_input('Escreva o seu prompt'):
    # --- Mostrar a menssagem do usuário na tela --- #
    with st.chat_message('user'):
        st.markdown(prompt)

    # --- Adicionar a menssagem do usuário ao histórico do chat --- #
    st.session_state.messages.append({'role': 'user', 'content': prompt})

    # --- Mostrar a resposta do bot ---#
    with st.chat_message('assistant'):
        resposta = st.write_stream(gerador_resposta(prompt))

    # --- Adicionar a resposta do bot no histórico do chat --- #
    st.session_state.messages.append({'role': 'assistant', 'content': resposta})