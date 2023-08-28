# Import packages
import os
import chainlit as cl
from gcloud import connect_gcloud
from chain import get_id_from_link, load_llm

TOKEN_PATH = os.path.join(os.getcwd(), 'token.json')


@cl.author_rename
def rename(orig_author: str):
    rename_dict = {"ConversationalRetrievalChain": "Minian AI"}
    return rename_dict.get(orig_author, orig_author)


@cl.action_callback("Connect Drive")
async def on_action_drive(action):
    url = connect_gcloud()
    await cl.Message(
        content=f"Please visit this URL to authorize this application: {url} ").send()
    await action.remove()
    await query_input()


async def query_input():
    res = await cl.AskUserMessage(
        content="Input a folder link to query...",
        timeout=1000).send()

    if res:
        folder_id = get_id_from_link(res['content'])
        content = f"Processing folder {folder_id}"
        msg = cl.Message(content=content)
        await msg.send()
        
        load_llm(folder_id)

        content = "We're ready to serve you. Ask your question"
        msg.content = content
        msg.author = 'Chatbot'
        await msg.update()


@cl.on_chat_start
async def start():

    await cl.Avatar(
        name = "Chatbot",
        url = "https://cdn-icons-png.flaticon.com/512/8649/8649595.png"
    ).send()
    await cl.Avatar(
        name = "Error",
        url = "https://cdn-icons-png.flaticon.com/512/8649/8649595.png"
    ).send()
    await cl.Avatar(
        name = "User",
        url = "https://media.architecturaldigest.com/photos/5f241de2c850b2a36b415024/master/w_1600%2Cc_limit/Luke-logo.png"
    ).send()

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
