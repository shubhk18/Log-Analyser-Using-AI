#!/bin/bash

# Script to start an Ollama chat session with a log file as context.
# This script creates a temporary Ollama model with the log content
# embedded in its system prompt, runs it interactively, and then cleans up.
#
# Usage:
#   ./start_chat.sh [base_model] [log_file_name]
#
# Examples:
#   ./start_chat.sh
#   ./start_chat.sh mistral
#   ./start_chat.sh llama3 mysql_connection_detailed.log

# --- Configuration ---
DEFAULT_MODEL="llama3.2:latest"
DEFAULT_LOG_FILE="mysql_connection.log"
SERVER_BASE_URL="http://localhost:8000/log"
TEMP_MODEL_NAME="gemini-log-chat-temp"
MODELFILE_PATH="./Modelfile.gemini-log-chat"

# --- Argument Handling ---
BASE_MODEL=${1:-$DEFAULT_MODEL}
LOG_FILE_NAME=${2:-$DEFAULT_LOG_FILE}
LOG_URL="$SERVER_BASE_URL/$LOG_FILE_NAME"

# --- Cleanup Function ---
# This function is called on script exit to clean up temporary files and models.
cleanup() {
  echo -e "\n\nCleaning up..."
  # Silently delete the temporary model
  ollama delete "$TEMP_MODEL_NAME" >/dev/null 2>&1
  # Remove the temporary Modelfile
  rm -f "$MODELFILE_PATH"
  echo "Cleanup complete. You can run the script again anytime."
}

# Set a trap to call the cleanup function on script exit (EXIT) or interrupt (INT).
trap cleanup EXIT INT

# --- Main Script ---
echo "Using base model: $BASE_MODEL"
echo "Fetching log from: $LOG_URL"
echo "----------------------------------------"

# Fetch Log Content
LOG_CONTEXT=$(curl -s --fail "$LOG_URL")

# Check if curl was successful
if [ $? -ne 0 ]; then
    echo "Error: Failed to fetch log content from $LOG_URL"
    echo "Please ensure the Python server ('python3 mcp_server.py') is running."
    exit 1
fi

# Escape special characters in the log content to safely embed it in the Modelfile.
ESCAPED_LOG_CONTEXT=$(echo "$LOG_CONTEXT" | sed 's/"/\\"/g')

# Create the Modelfile. This defines a new model that has the log as part of its system prompt.
cat > "$MODELFILE_PATH" << EOL
FROM $BASE_MODEL

SYSTEM """
You are a helpful log analysis assistant. The user has provided a log file below for context. Your task is to answer the user's questions based *only* on the information contained within this log.

When the session begins, greet the user, briefly confirm that you have loaded the log file, and state that you are ready to answer questions about it.

--- LOG FILE START ---
$ESCAPED_LOG_CONTEXT
--- LOG FILE END ---
"""
EOL

echo "Creating temporary model with log context..."
# Create the temporary model. Output is hidden for a cleaner experience.
ollama create "$TEMP_MODEL_NAME" -f "$MODELFILE_PATH" >/dev/null

echo "Model '$TEMP_MODEL_NAME' created."
echo "Starting interactive chat session..."
echo "----------------------------------------"
echo "Type '/bye' or press Ctrl+D to exit the chat and clean up."
echo

# Run the temporary model, which will now start in interactive mode.
ollama run "$TEMP_MODEL_NAME"

# The 'trap' will handle the cleanup automatically when the user exits the chat.