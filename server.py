import chainlit as cl
from gcloud import connect_gcloud
from chain import load_llm

import os
TOKEN_PATH = os.path.join(os.getcwd(), 'token.json')


def get_folder_id_from_link(folder_link):
    splits = folder_link.split('/')
    return splits[-1]


@cl.action_callback("Connect Drive")
async def on_action(action):
    connect_gcloud()
    await cl.Message(content="Drive connected").send()
    await action.remove()


@cl.on_chat_start
async def on_start():

    if not os.path.exists(TOKEN_PATH):
        actions = [
            cl.Action(name="Connect Drive", value="",
                      description="Connect Drive")
        ]
        await cl.Message(content="Click this button to connect drive",
                         actions=actions).send()

    res = await cl.AskUserMessage(content="Please enter a folder link to query",
                                  timeout=10).send()
    if res:
        folder_id = get_folder_id_from_link(res['content'])
        await cl.Message(
            content=f"Picked folder with id {folder_id}",
        ).send()
        load_llm(folder_id)


@cl.on_message
async def main(question, chat):

    llm_chain = cl.user_session.get("llm_chain")
    res = await llm_chain.acall({"question": question},
                                callbacks=[cl.AsyncLangchainCallbackHandler()])

    await cl.Message(content=res["answer"]).send()
