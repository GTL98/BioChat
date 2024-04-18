# --- Importar as bibliotecas --- #
from langchain.agents import AgentExecutor
from langchain.tools import WikipediaQueryRun
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatCohere
from langchain_core.prompts import MessagesPlaceholder
from langchain_cohere import create_cohere_react_agent
from langchain_community.embeddings import CohereEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.tools.retriever import create_retriever_tool
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.chains.retrieval import create_retrieval_chain
from langchain_community.tools.pubmed.tool import PubmedQueryRun
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever



class BioChat:
    """
    Classe responsável por criar o chat.
    """
    def __init__(self, prompt: str):
        """
        Função responsável por inicializar a classe.
        :param prompt: Prompt do usuário
        """
        # --- Prompt --- #
        self.prompt = prompt

        # --- API do Cohere --- #
        self.api_chat = ChatCohere(cohere_api_key='JSBKdvdzP4xI00kBiJ5NvitpFITBdb0jbMCC5Z1R')

        # --- API do embedding --- #
        self.api_embedding = CohereEmbeddings(cohere_api_key='JSBKdvdzP4xI00kBiJ5NvitpFITBdb0jbMCC5Z1R')

        # --- API da Wikipedia --- #
        self.api_wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())

        # --- API do PubMed --- #
        self.api_pubmed = PubmedQueryRun()

    def carregar_pdf(self):
        """
        Função responsável por carregar o PDF.
        :return: Objeto com as páginas do PDF.
        """
        # --- Carregar o arquivo PDF --- #
        carregador = PyPDFLoader('Apostila - Introdução à Bioinformática.pdf')

        # --- Obter as páginas --- #
        paginas = carregador.load_and_split()

        return paginas

    def criar_vetor_pdf(self):
        """
        Função responsável por criar o vetor do PDF.
        :return:
        """
        # --- Criar a variável das páginas --- #
        paginas = self.carregar_pdf()

        # --- Criar o vetor --- #
        vetor = FAISS.from_documents(paginas, self.api_embedding)

        return vetor

    def criar_retriever(self):
        """
        Função responsável por criar o retriever.
        :return: Lista com o cadeia do documento, retriever e o template.
        """
        # --- Criar o template para o contextualizar o chat --- #
        template = ChatPromptTemplate.from_messages(
            [
                ("system", "Você é um profissional de bioinformática com didática excepcional, proativo e muito antencioso. Faça respostas completas, focando em leigos. Responda apenas perguntas de bioinformática e programação. Responda para leigos. Utilize a apostila de bioinformática apenas em extrema necessidade, procure antes na internet. Utilize em todas as suas respostas markdown em suas respostas para destacar, com negrito, palavras-chave importantes e fazer títulos. Se o usuário pedir, faça códigos de linguagem de programação seguindo as boas práticas da programação, encontre sempre uma oportunidade de mostrar um exemplo de código, mas sinalize que, como uma IA, é importante que não confiem completamente em seu código. Dê exemplos reais de todos os arquivos e linguagens de programação solicitados. Para perguntas fora do escopo de bioinformática, desculpe-se ao usuário e não responda a pergunta. Answer the user's questions based on the below context:\n\n{context}"),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{input}")
            ]
        )

        # --- Criar a variável do vetor do PDF --- #
        vetor = self.criar_vetor_pdf()

        # --- Criar a cadeia do documento --- #
        cadeia_documento = create_stuff_documents_chain(self.api_chat, template)

        # --- Criar o retriever --- #
        retriever = vetor.as_retriever()

        return cadeia_documento, retriever, template

    def criar_ferramenta_retriever(self):
        """
        Função responsável por criar a ferramenta do retriever para o agente.
        :return: Ferramente do retriever.
        """
        # --- Criar a variável do retriever --- #
        retriever = self.criar_retriever()[1]

        # --- Criar a ferramenta --- #
        ferramenta = create_retriever_tool(
            retriever,
            "bioinfo_search",
            "Apostila de Bioinformática. Contém informações de ferramentas e conceitos básicos de bioinformática. Utilize-o para procurar sobre Genbank, Fasta, Bioedit, Phylogeny.fr, Artemis, Artemis Comparission Tool, ORF Finder, NCBI, UniProt, PDB",
        )

        return ferramenta

    def criar_agente(self):
        """
        Função responsável por criar o agente do chat.
        :return: O executador do agente.
        """
        # --- Criar a variável da ferramenta do retriever --- #
        ferramenta = self.criar_ferramenta_retriever()

        # --- Criar o template do agente --- #
        template_agente = ChatPromptTemplate.from_messages([
            ("system",
             "Seu nome é BioChat. Você é um profissional de bioinformática com didática excepcional, proativo e muito antencioso. Faça respostas completas, focando em leigos. Responda apenas perguntas de bioinformática e programação. Utilize a apostila de bioinformática apenas em extrema necessidade. Utilize em todas as suas respostas markdown em suas respostas para destacar, com negrito, palavras-chave importantes e fazer títulos. Divida os parágrafos com novas linhas, quando der exemplo de códigos faça uma nova linha antes de começar o exemplo e depois de terminá-lo e preserve as quebras de linha necessárias ao longo do código, mantendo sua legibilidade e compreensão. Se o usuário pedir, faça códigos de linguagem de programação seguindo as boas práticas da programação, encontre sempre uma oportunidade de mostrar um exemplo de código, mas sinalize que, como uma IA, é importante que não confiem completamente em seu código. Sempre dê exemplos reais de todos os arquivos e linguagens de programação solicitados. Para perguntas fora do escopo de bioinformática, desculpe-se ao usuário e não responda a pergunta"),
            ("user", "{input}")
        ])
        # --- Criar o agente --- #
        agente = create_cohere_react_agent(
            self.api_chat,
            [
                ferramenta,
                self.api_wikipedia,
                self.api_pubmed
            ],
            template_agente
        )

        # --- Criar o executor do agente --- #
        executador_agente = AgentExecutor(
            agent=agente,
            tools=[
                ferramenta,
                self.api_wikipedia,
                self.api_pubmed
            ],
            verbose=False
        )

        return executador_agente

    def criar_historico_agente(self):
        """
        Função responsável por criar o histórico do agente.
        :return: O agente com histórico.
        """
        # --- Chamar o agente --- #
        agente = self.criar_agente()

        # --- Criar o histórico de mensagens --- #
        mensagens_historico = ChatMessageHistory()

        # --- Criar o agente com o histórico --- #
        agente_com_historico = RunnableWithMessageHistory(
            agente,
            lambda session_id: mensagens_historico,
            input_messages_key='input',
            history_messages_key='chat_history'
        )

        return agente_com_historico

    def criar_reposta(self):
        """
        Função responsável por gerar a resposta.
        :return: Rsposta do chat.
        """
        # --- Chamar o agente com histórico --- #
        agente = self.criar_historico_agente()

        # --- Criar a resposta --- #
        resposta = agente.invoke(
            {'input': self.prompt},
            config={
                'configurable': {'session_id': '<foo>'}
            }
        )

        # --- Resposta final --- #
        resposta_final = resposta['output']

        return resposta_final
