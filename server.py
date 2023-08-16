import chainlit as cl
from gcloud import connect_gcloud
from chain import load_llm

import os
TOKEN_PATH = os.path.join(os.getcwd(), 'token.json')


@cl.action_callback("Connect Drive")
async def on_action(action):
    connect_gcloud()
    await cl.Message(content="Drive connected").send()
    await action.remove()
    load_llm()
    await cl.Message(content="We're ready to serve you. Ask you question",
                     ).send()
    print('Gcloud connected. LLM loading done')


@cl.on_chat_start
async def on_start():
    cl.Message(content="Wait until we finish setting up system",
               ).send()
    if not os.path.exists(TOKEN_PATH):
        actions = [
            cl.Action(name="Connect Drive", value="",
                      description="Connect Drive")
        ]
        await cl.Message(content="Click this button to connect drive",
                         actions=actions).send()
    else:
        load_llm()
        await cl.Message(content="We're ready to serve you. Ask you question",
                         ).send()
        print('LLM loading done')


@cl.on_message
async def main(question, chat):

    llm_chain = cl.user_session.get("llm_chain")
    res = await llm_chain.acall({"question": question},
                                callbacks=[cl.AsyncLangchainCallbackHandler()])

    await cl.Message(content=res["answer"]).send()
