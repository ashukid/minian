# Import packages
import os
import chainlit as cl
from gcloud import connect_gcloud
from chain import get_id_from_link, load_llm


@cl.author_rename
def rename(orig_author: str):
    rename_dict = {"ConversationalRetrievalChain": "Minian AI"}
    return rename_dict.get(orig_author, orig_author)


async def query_input(username):

    res = None
    while res == None:
        res = await cl.AskUserMessage(
            content="Input a folder link to query...",
            timeout=86400).send()

    folder_id = get_id_from_link(res['content'])
    content = f"Processing folder {folder_id}"
    msg = cl.Message(content=content)
    await msg.send()

    load_llm(folder_id, username)

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

    res = None
    while res == None:
        res = await cl.AskUserMessage(
            content="Please input your username...",
            timeout=86400).send()

    username = res['content']
    token_path = os.path.join(username, 'token.json')
    if not os.path.exists(token_path):
        url = connect_gcloud(username)
        await cl.Message(
            content=f"Please visit this URL to authorize this application: {url} ").send()

    await query_input(username)


@cl.on_message
async def main(question):

    llm_chain = cl.user_session.get("llm_chain")
    if llm_chain:
        res = await llm_chain.acall(
            {"question": question},
            callbacks=[cl.AsyncLangchainCallbackHandler()])

        await cl.Message(content=res["answer"]).send()
