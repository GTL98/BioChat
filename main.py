# ToDo: https://docs.streamlit.io/knowledge-base/tutorials/build-conversational-apps#build-a-chatgpt-like-app
# --- Importar a biblioteca --- #
import streamlit as st

# --- Configuração da página --- #
st.set_page_config(
    page_title='BioChat',
    layout='centered'
)

# --- Título à página --- #
st.title('BioChat :speech_balloon::dna:')

# --- Criar uma lista para armazenar o histórico do usuário --- #
if 'mensagens' not in st.session_state:
    st.session_state['mensagens'] = []

# --- Criar a caixa de perguntas e respostas --- #
with st.chat_message('assistant'):
    st.write('Olá, bioinformata! Como posso ajudá-lo?')

# --- Criar a caixa de entrada do usuário --- #
entrada = st.chat_input('Digite o seu prompt')
if entrada:
    st.write(f'O usuário digitou: {entrada}')