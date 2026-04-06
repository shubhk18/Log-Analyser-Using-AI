# Log Analyser

This project provides tools for analyzing log files, offering both direct AI chat interaction and production-grade log mining for high-volume systems.

## Architecture

The application consists of several key components:

*   `mcp_server.py`: A Python script that creates an HTTP server to serve log files, making them accessible to other tools.
*   `chat_ai.py`: A **generic** Python client that uses `litellm` to connect to any LLM provider (Ollama, Gemini, OpenAI, etc.), allowing you to chat with log content.
*   `template_miner.py`: A script designed for production environments that mines log templates in real-time using **Drain3** and indexes them with **FAISS**, efficiently handling high-volume logs.
*   `log_generator.py`: A utility script to generate sample log files for testing.
*   **Log files**: Plain text files containing log data (e.g., `mysql_connection.log`, `detailed_log.txt`).

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
└── template_miner.py
```

## Setup

1.  **Create and activate a virtual environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On macOS/Linux
    # venv\Scripts\activate   # On Windows
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure LLM** (Optional):
    Copy `.env.example` to `.env` and set your preferred model and API keys.
    ```bash
    cp .env.example .env
    ```
    *   `LLM_MODEL`: Set your preferred LLM (e.g., `ollama/llama3.2:latest`, `gemini/gemini-1.5-flash`).
    *   API keys are needed for cloud providers.

## How to run

### 1. Log Server
Start the server that provides log files to `chat_ai.py`:
```bash
python3 mcp_server.py
```
*(Keep this running in a separate terminal or in the background)*

### 2. AI Chat Client (`chat_ai.py`)
This script allows you to chat with log content using any LLM provider supported by `litellm`.

```bash
# Analyze the default log file (mysql_connection.log) with the default model
python3 chat_ai.py

# Specify a log file to analyze
python3 chat_ai.py detailed_log.txt

# Specify a model (e.g., Gemini)
python3 chat_ai.py --model gemini/gemini-1.5-flash

# Specify a model and a log file
python3 chat_ai.py detailed_log.txt --model gemini/gemini-1.5-flash
```

### 3. Production Log Miner (`template_miner.py`)
This script mines unique log templates in real-time using Drain3 and indexes them with FAISS, making it efficient for production log analysis.

```bash
# Ensure logs exist (run log_generator.py if needed)
python3 log_generator.py

# Run the template miner
python3 template_miner.py
```
*Observe how it discovers unique log templates as new lines are added to `mysql_connection.log`.*

---

## Testing Workflow (End-to-End Simulation)

To test the complete log analysis pipeline, simulating a production environment:

1.  **Setup Environment:**
    ```bash
    # 1. Create and activate venv
    python3 -m venv venv
    source venv/bin/activate
    
    # 2. Install dependencies
    pip install -r requirements.txt
    
    # 3. Configure LLM (optional, e.g., for Ollama)
    # cp .env.example .env 
    # (Ensure LLM_MODEL is set correctly, e.g., ollama/llama3.2:latest)
    ```

2.  **Start Services:**
    *   **Terminal 1: Log Server**
        ```bash
        python3 mcp_server.py
        ```
        *(Keep this running)*

    *   **Terminal 2: Log Generator (Optional, to simulate dynamic log flow)**
        ```bash
        python3 log_generator.py
        ```
        *(You can run this periodically or in parallel with the miner to simulate continuous log flow. It will generate logs into `mysql_connection.log`.)*

3.  **Run the Indexer:**
    *   **Terminal 3: Template Miner**
        ```bash
        python3 template_miner.py
        ```
        *(Watch as it discovers and indexes unique log templates from `mysql_connection.log`.)*

4.  **Start Chat Analysis:**
    *   **Terminal 4: AI Chat Client**
        ```bash
        # Analyze a specific log file
        python3 chat_ai.py mysql_connection.log 
        
        # Or use the default log and model
        # python3 chat_ai.py 
        ```
        *(Ask questions about the logs. The AI will use the context provided by `chat_ai.py`.)*

---

## Log Mining Workflow (Isolated Test)

To specifically test the log mining capabilities of `template_miner.py`:

1.  **Ensure Logs Exist:**
    Run `python3 log_generator.py` to create or update `mysql_connection.log`.
2.  **Run Template Miner:**
    ```bash
    python3 template_miner.py
    ```
    *Observe the output showing "New Template Found" as it processes existing and incoming log lines.*
3.  **Interact (Optional):**
    While `template_miner.py` is running, you can use `chat_ai.py` to query the log. The `template_miner` updates the FAISS index asynchronously.

---

## Data Flow

1.  **Log Generation:** `log_generator.py` (or a real production system) creates log files.
2.  **Log Serving:** `mcp_server.py` makes these logs accessible via HTTP.
3.  **Real-time Indexing:** `template_miner.py` tails the log file:
    *   Uses **Drain3** to extract log templates.
    *   Embeds only **unique** templates.
    *   Stores templates and their embeddings in **FAISS**.
4.  **AI Chat Analysis:** `chat_ai.py` fetches log content from the server, constructs a prompt, and sends it to the configured LLM (Ollama, Gemini, etc.) via `litellm`.
5.  **LLM Reasoning:** The LLM analyzes the provided context (either raw logs or template-derived information) to answer user questions.

---

## External Tools and Licenses

*   **OLLAMA**: Used for running language models locally. It is open-source and distributed under the **MIT License**.
*   **curl**: A command-line tool used for transferring data with URLs. It is distributed under a permissive open-source license, similar to the **MIT/X license**.
*   **litellm**: For generic LLM provider access.
*   **Drain3**: For log template mining.
*   **FAISS**: For efficient vector similarity search.
*   **Python**: Standard library.
