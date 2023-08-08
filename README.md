# minian 🚀🤖
Hi there, minian is a simple app to query your google drive files


## Setup

1. Create a `.env` file in your project root, copy the variables from `.env.sample`, and change their values.
2. Install python dependencies:

```
pip install -r requirements.txt
```

3. Install system dependencies ( refer to this page - https://python.langchain.com/docs/integrations/document_loaders/unstructured_file)

```
brew install libmagic
```

4. Download and save credentials.json in the root directory (https://console.cloud.google.com/apis/credentials)


## Usage

- Run following command to fire up the website :

```
chainlit run server.py -w
```

- Website is setup to run on port 8000
- You can check the Readme on the webpage to get more info







