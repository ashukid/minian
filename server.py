from langchain.document_loaders import GoogleDriveLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
import chainlit as cl
import os
from google_auth_oauthlib.flow import InstalledAppFlow

TOKEN_PATH = os.path.join(os.getcwd(),'token.json')


def get_folder_id_from_link(folder_link):
    splits = folder_link.split('/')
    return splits[-1]


def load_llm(folder_id):
    template = """Use the following pieces of context to answer the question at the end. 
    If you don't know the answer, just say that you don't know, don't try to make up an answer. 
    Use three sentences maximum and keep the answer as concise as possible. 
    Always say "thanks for asking!" at the end of the answer. 
    {context}
    Question: {question}
    Helpful Answer:"""
    QA_CHAIN_PROMPT = PromptTemplate.from_template(template)

    loader = GoogleDriveLoader(
        folder_id=folder_id,
        token_path=TOKEN_PATH,
        recursive=False,
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


def connect_gcloud():
    # connect
    SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
    flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    with open('token.json', 'w') as token:
        token.write(creds.to_json())


@cl.action_callback("Connect Drive")
async def on_action(action):
    connect_gcloud()
    await cl.Message(content="Drive connected").send()
    await action.remove()


@cl.on_chat_start
async def on_start():

    if not os.path.exists(TOKEN_PATH):
        actions = [
            cl.Action(name="Connect Drive", value="", description="Connect Drive")
        ]
        await cl.Message(content="Click this button to connect drive", actions=actions).send()

    res = await cl.AskUserMessage(content="Please enter a folder link to query", timeout=10).send()
    if res:
        folder_id = get_folder_id_from_link(res['content'])
        load_llm(folder_id)
        await cl.Message(
            content=f"Picked folder with id {folder_id}",
        ).send()


@cl.on_message
async def main(question, chat):

    llm_chain = cl.user_session.get("llm_chain")
    res = await llm_chain.acall({"question": question},
                                callbacks=[cl.AsyncLangchainCallbackHandler()])

    await cl.Message(content=res["answer"]).send()
