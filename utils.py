import time
import tiktoken
import os
from langchain.vectorstores import Chroma

PERSIST_DIRECTORY = "db"


def count_tokens(input: str) -> int:
    token_encoding = tiktoken.get_encoding("cl100k_base")
    return len(token_encoding.encode(input))


def _split_docs_by_token_count(docs, max_tokens):
    output_list = []
    sublist = []
    token_count = 0
    for doc in docs:
        current_doc_token_count = count_tokens(doc.page_content)
        if token_count + current_doc_token_count < max_tokens:
            sublist.append(doc)
            token_count += current_doc_token_count
        else:
            output_list.append(sublist)
            sublist = [doc]
            token_count = current_doc_token_count
    # Add the last sublist
    if sublist:
        output_list.append(sublist)
    return output_list


# TODO: This method should be called within the base class
def _index_to_vectorstore(docs, embeddings, username):

    MAX_TOKENS_PER_MINUTE = 250000
    docs_list = _split_docs_by_token_count(
        docs, MAX_TOKENS_PER_MINUTE)
    for i, doc_set in enumerate(docs_list):
        print(f'Processing document - {i}')
        if i != 0:
            time.sleep(60)
        Chroma.from_documents(doc_set,
                              embeddings,
                              persist_directory=os.path.join(username, 'db'))
