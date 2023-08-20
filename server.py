import chainlit as cl
from gcloud import connect_gcloud
from chain import load_llm, get_id_from_link

import os
TOKEN_PATH = os.path.join(os.getcwd(), 'token.json')


@cl.author_rename
def rename(orig_author: str):
    rename_dict = {"ConversationalRetrievalChain": "Minian AI",
                   "Chatbot": "Minian"}
    return rename_dict.get(orig_author, orig_author)


async def query_input():
    res = await cl.AskUserMessage(
        content="Input a folder link to query...", timeout=10).send()

    if res:
        folder_id = get_id_from_link(res['content'])
        load_llm(folder_id)
        await cl.Message(
            content="We're ready to serve you. Ask your question").send()


@cl.action_callback("Connect Drive")
async def on_action_drive(action):
    connect_gcloud()
    await cl.Message(
        content="Drive connected successfully").send()
    await action.remove()
    await query_input()


@cl.on_chat_start
async def on_start():
    if not os.path.exists(TOKEN_PATH):
        actions = [
            cl.Action(name="Connect Drive", value="",
                      description="Connect Drive")
        ]
        await cl.Message(content="Click this button to connect drive",
                         actions=actions).send()
    else:
        await query_input()


@cl.on_message
async def main(question):

    llm_chain = cl.user_session.get("llm_chain")
    if llm_chain:
        res = await llm_chain.acall(
            {"question": question},
            callbacks=[cl.AsyncLangchainCallbackHandler()])

        await cl.Message(content=res["answer"]).send()
