import chainlit as cl
from langchain.document_loaders import GoogleDriveLoader
from langchain.document_loaders import UnstructuredFileIOLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
import os
import tiktoken
from utils import _index_to_vectorstore


# openai / langchain Const
RETRIEVER_K_ARG = 3
OPENA_AI_MODEL = "gpt-4-0314"
PERSIST_DIRECTORY = "db"
TOKEN_PATH = os.path.join(os.getcwd(), 'token.json')
CREDS_PATH = os.path.join(os.getcwd(), 'credentials.json')


def count_tokens(input: str) -> int:
    token_encoding = tiktoken.get_encoding("cl100k_base")
    return len(token_encoding.encode(input))


def get_id_from_link(folder_link):
    splits = folder_link.split('/')
    return splits[-1]


def load_documents(folder_id):
    loader = GoogleDriveLoader(
        folder_id=folder_id,
        recursive=True,
        token_path=TOKEN_PATH,
        credentials_path=CREDS_PATH,
        file_loader_cls=UnstructuredFileIOLoader
    )
    return loader.load()


def split_documents(docs):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500,
                                                   chunk_overlap=200)

    return text_splitter.split_documents(docs)


def load_chroma_db(embeddings):
    return Chroma(embedding_function=embeddings,
                  persist_directory=PERSIST_DIRECTORY)


def create_retriever(db):
    return db.as_retriever(search_kwargs={"k": RETRIEVER_K_ARG})


def create_llm():
    return ChatOpenAI(temperature=0,
                      model_name=OPENA_AI_MODEL)


def create_prompt():
    template = """Use the context to answer the question.
    {context}
    Question: {question}
    Helpful Answer:"""
    return PromptTemplate.from_template(template)


def create_index(llm, retriever, prompt):
    memory = ConversationBufferMemory(memory_key="chat_history",
                                      return_messages=True)
    return ConversationalRetrievalChain.from_llm(llm,
                                                 retriever=retriever,
                                                 memory=memory,
                                                 combine_docs_chain_kwargs={
                                                     "prompt": prompt
                                                     })


def load_llm(folder_id):
    embeddings = OpenAIEmbeddings()
    docs = load_documents(folder_id)
    texts = split_documents(docs)
    _index_to_vectorstore(texts, embeddings)
    db = load_chroma_db(embeddings)
    retriever = create_retriever(db)
    llm = create_llm()
    prompt = create_prompt()
    qa = create_index(llm, retriever, prompt)
    cl.user_session.set("llm_chain", qa)
