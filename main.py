# Import packages
import os
import chainlit as cl
from chainlit import make_async
from gcloud import connect_gcloud
from chain import get_id_from_link, load_llm

# Define a constant for the bot's avatar URL
BOT_AVATAR_URL = "https://cdn-icons-png.flaticon.com/512/8649/8649595.png"

# Define a constant for the user's avatar URL
USER_AVATAR_URL = "https://media.architecturaldigest.com/photos/5f241de2c850b2a36b415024/master/w_1600%2Cc_limit/Luke-logo.png"


@cl.author_rename
def rename(orig_author: str):
    rename_dict = {"ConversationalRetrievalChain": "Minian AI"}
    return rename_dict.get(orig_author, orig_author)


@cl.on_chat_start
async def start():
    # Set avatars for Chatbot, Error, and User
    await cl.Avatar(name="Chatbot", url=BOT_AVATAR_URL).send()
    await cl.Avatar(name="Error", url=BOT_AVATAR_URL).send()
    await cl.Avatar(name="User", url=USER_AVATAR_URL).send()

    res = None
    while res is None:
        res = await cl.AskUserMessage(
            content="Please input your username...",
            timeout=86400
        ).send()

    username = res['content']
    token_path = os.path.join(username, 'token.json')
    if not os.path.exists(token_path):
        url = await make_async(connect_gcloud)(username)
        await cl.Message(
            content=f"Please visit this URL to authorize this application: {url} "
        ).send()

    res = None
    while res is None:
        res = await cl.AskUserMessage(
            content="Input a folder link to query...",
            timeout=86400
        ).send()

    folder_id = get_id_from_link(res['content'])
    content = f"Processing folder {folder_id}"
    # Create a message with bot's avatar
    msg = cl.Message(content=content, author="Chatbot")
    await msg.send()

    # Load LLM using ThreadPoolExecutor
    await load_llm(folder_id, username)

    content = "We're ready to serve you. Ask your question"
    msg.content = content
    await msg.update()


@cl.on_message
async def main(question):
    llm_chain = cl.user_session.get("llm_chain")
    res = await llm_chain.acall(
        {"question": question},
        callbacks=[cl.AsyncLangchainCallbackHandler()]
    )

    await cl.Message(content=res["answer"]).send()
