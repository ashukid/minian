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
TOKEN_PATH = os.path.join(os.getcwd(),'token.json')


def load_llm(folder_id):
    template = """Use the following pieces of context to answer the
    question at the end. If you don't know the answer, just say that
    you don't know, don't try to make up an answer.
    Use three sentences maximum and keep the answer as concise as possible.
    Always say "thanks for asking!" at the end of the answer.
    {context}
    Question: {question}
    Helpful Answer:"""
    QA_CHAIN_PROMPT = PromptTemplate.from_template(template)

    loader = GoogleDriveLoader(
        folder_id=folder_id,
        token_path=TOKEN_PATH,
        file_loader_cls=UnstructuredFileIOLoader
    )
    data = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500,
                                                   chunk_overlap=0)
    all_splits = text_splitter.split_documents(data)
    vectorstore = Chroma.from_documents(documents=all_splits,
                                        embedding=OpenAIEmbeddings())
    memory = ConversationBufferMemory(memory_key="chat_history",
                                      return_messages=True)
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    retriever = vectorstore.as_retriever()
    chat = ConversationalRetrievalChain.from_llm(llm,
                                                 retriever=retriever,
                                                 memory=memory,
                                                 combine_docs_chain_kwargs={
                                                     "prompt": QA_CHAIN_PROMPT
                                                     })
    cl.user_session.set("llm_chain", chat)
