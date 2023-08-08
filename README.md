# MiniAn - Google Drive Query App 🚀🤖

MiniAn allows you to easily query your Google Drive files through a simple and intuitive interface.

## 📋 Prerequisites

- **Python:** Ensure you have Python installed with `pip`.
- **Homebrew:** This is required for macOS users.

## 🔧 Setup

### 1. Environment Variables

- Create a `.env` file in the root directory of your project.
- Copy all the variables from `.env.sample` into the `.env` file.
- Update the variables in `.env` with the appropriate values.

### 2. Python Dependencies

Install the required Python packages using:

```bash
pip install -r requirements.txt
```

### 3. System Dependencies

For detailed instructions on system dependencies, refer to the [documentation](https://python.langchain.com/docs/integrations/document_loaders/unstructured_file).

For macOS users:

```bash
brew install libmagic
```

### 4. Google Drive Credentials

1. Navigate to the [Google Cloud Console](https://console.cloud.google.com/apis/credentials).
2. Download the `credentials.json` file.
3. Place `credentials.json` in the root directory of your project.

## 🚀 Usage

To launch the MiniAn web application, execute the following command:

```bash
chainlit run server.py -w
```

