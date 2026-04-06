import os
import sys
import requests
import argparse
from litellm import completion
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# --- Configuration ---
DEFAULT_MODEL = os.getenv("LLM_MODEL", "ollama/llama3.2")
SERVER_BASE_URL = os.getenv("LOG_SERVER_URL", "http://localhost:8000/log")

def fetch_log(log_name):
    """Fetches log content from the mcp_server."""
    url = f"{SERVER_BASE_URL}/{log_name}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to fetch log from {url}")
        print(f"Details: {e}")
        print("\nMake sure 'python3 mcp_server.py' is running.")
        sys.exit(1)

def start_chat(log_content, model_name):
    """Starts an interactive chat session with the log content as context."""
    
    # Initialize the conversation with the log context in the system prompt
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful log analysis assistant. The user has provided a log file below for context. "
                "Your task is to answer the user's questions based *only* on the information contained within this log.\n\n"
                "--- LOG FILE START ---\n"
                f"{log_content}\n"
                "--- LOG FILE END ---\n"
            )
        }
    ]

    print(f"\n--- Log context loaded. Model: {model_name} ---")
    print("Type 'exit' or 'quit' to end the session.\n")

    # Initial greeting
    try:
        response = completion(model=model_name, messages=messages)
        answer = response.choices[0].message.content
        print(f"AI: {answer}\n")
        messages.append({"role": "assistant", "content": answer})
    except Exception as e:
        print(f"Error during initial connection: {e}")
        return

    # Chat loop
    while True:
        try:
            user_input = input("You: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "/bye"]:
                print("Goodbye!")
                break

            messages.append({"role": "user", "content": user_input})
            
            # Call the LLM (Litellm handles switching between providers)
            response = completion(model=model_name, messages=messages)
            answer = response.choices[0].message.content
            
            print(f"\nAI: {answer}\n")
            messages.append({"role": "assistant", "content": answer})
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="Chat with log files using AI.")
    parser.add_argument("log_file", nargs="?", default="mysql_connection.log", help="Name of the log file to analyze.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"LLM model to use (default: {DEFAULT_MODEL}).")
    
    args = parser.parse_args()

    # If no provider prefix is provided (e.g. "llama3" instead of "ollama/llama3"), 
    # assume it's an Ollama model for local-first convenience.
    model_name = args.model
    if "/" not in model_name:
        model_name = f"ollama/{model_name}"

    # Step 1: Fetch the log
    print(f"Fetching log: {args.log_file}...")
    log_content = fetch_log(args.log_file)

    # Step 2: Start the chat session
    start_chat(log_content, model_name)

if __name__ == "__main__":
    main()
