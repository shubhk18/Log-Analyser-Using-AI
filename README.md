# Log_Analyser

## Architecture

The application consists of three main components:

*   `mcp_server.py`: A Python script that creates an HTTP server to serve log files.
*   `chat_ai.py`: A **generic** Python client that uses `litellm` to connect to any LLM provider (Ollama, Gemini, OpenAI, etc.).
*   `start_chat.sh`: (Legacy) A shell script specifically for local Ollama usage.
*   **Log files**: Plain text files containing log data.

## File Hierarchy

```
.
├── .env.example
├── .gitignore
├── chat_ai.py
├── detailed_log.txt
├── log_generator.py
├── mcp_server.py
├── Modelfile.gemini-log-chat
├── mysql_connection.log
├── README.md
├── requirements.txt
└── start_chat.sh
```

## Setup

1.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Configure LLM** (Optional):
    Copy `.env.example` to `.env` and set your preferred model and API keys.
    ```bash
    cp .env.example .env
    ```

## How to run

1.  **Start the server**:
    ```bash
    python3 mcp_server.py
    ```
2.  **Start the chat session**:
    ```bash
    # Use default model (defined in .env or Ollama)
    python3 chat_ai.py

    # Specify a model (e.g., Gemini)
    python3 chat_ai.py --model gemini/gemini-1.5-flash

    # Specify a log file
    python3 chat_ai.py detailed_log.txt
    ```

## Data Flow

1.  The user runs the `mcp_server.py` script, which starts an HTTP server.
2.  The user runs the `start_chat.sh` script.
3.  The script fetches the specified log file from the running Python server using `curl`.
4.  A temporary OLLAMA model is created with the log file's content embedded in its system prompt.
5.  An interactive chat session is started with the temporary model.
6.  The user can now ask questions about the log file in the chat.
7.  When the chat is closed, the temporary model and its files are automatically cleaned up.


## Test Evidence
**MCP Server-**


**Log server-**
<img width="1532" height="901" alt="image" src="https://github.com/user-attachments/assets/1023e505-bcd9-42b1-916b-d35085aead30" />


**chat window-**
<img width="1550" height="889" alt="image" src="https://github.com/user-attachments/assets/c7da7445-89f5-44eb-b309-656179a5343c" />

## External Tools and Licenses

*   **OLLAMA**: Used for running language models locally. It is open-source and distributed under the **MIT License**.
*   **curl**: A command-line tool used for transferring data with URLs. It is distributed under a permissive open-source license, similar to the **MIT/X license**.
