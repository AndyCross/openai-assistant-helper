# OpenAI Assistant Manager

A command-line tool for managing OpenAI assistants and generating tips using their knowledge base. This tool allows you to create assistants, manage vector stores, upload files (individually or in bulk), and generate tips based on the assistant's knowledge.

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd openai-assistant-manager
```

2. Install dependencies using Poetry:
```bash
poetry install
```

3. Set up your environment variables by creating a `.env` file:
```bash
OPENAI_API_KEY=your_api_key_here
OPENAI_ORG_ID=your_organization_id_here
```

## Commands

### Create a Vector Store
Create a new vector store for file storage:
```bash
poetry run assistant-manager create-vector-store \
    "My Vector Store" \
    --description "Store for my assistant's files"
```

### Get Vector Store Info
Retrieve information about an existing vector store:
```bash
poetry run assistant-manager get-vector-store "My Vector Store"
```

### Create an Assistant
Create a new OpenAI assistant with a specified name and description. This automatically creates a matching vector store if it doesn't exist:
```bash
poetry run assistant-manager create-assistant \
    --name "Tip Generator" \
    --description "Generates daily tips" \
    --model "gpt-4-1106-preview"
```

### Upload a Single File
Upload an individual file to an assistant's knowledge base (automatically added to the assistant's vector store):
```bash
poetry run assistant-manager upload-file \
    path/to/file.docx \
    --assistant-id "asst_..."
```

### Upload Files from a Folder
Recursively upload files from a folder and its subfolders:
```bash
# Upload all .docx files (default)
poetry run assistant-manager upload-folder \
    ./my_documents \
    --assistant-id "asst_..."

# Upload specific file types
poetry run assistant-manager upload-folder \
    ./my_documents \
    --assistant-id "asst_..." \
    --pattern "*.pdf"
```

### Generate a Tip
Generate a tip using the assistant's knowledge base:
```bash
poetry run assistant-manager generate-tip \
    "productivity" \
    --assistant-id "asst_..." \
    --max-tokens 150
```

## Helper Shell Functions

Add these to your `~/.zshrc` for easier usage:

```bash
# Function to create a vector store
create-vector-store() {
    if [ -z "$1" ]; then
        echo "Usage: create-vector-store <name> [description]"
        return 1
    fi
    poetry run assistant-manager create-vector-store "$1" ${2:+--description "$2"}
}

# Function to get vector store info
get-vector-store() {
    if [ -z "$1" ]; then
        echo "Usage: get-vector-store <name>"
        return 1
    fi
    poetry run assistant-manager get-vector-store "$1"
}

# Function to set up a new assistant
assistant-setup() {
    poetry run assistant-manager create-assistant \
        --name "$1" \
        --description "$2" \
        --model "${3:-gpt-4-1106-preview}"
}

# Function to upload files
assistant-upload() {
    if [ -z "$1" ] || [ -z "$2" ]; then
        echo "Usage: assistant-upload <file_path> <assistant_id>"
        return 1
    fi
    poetry run assistant-manager upload-file "$1" --assistant-id "$2"
}

# Function to upload folders
assistant-upload-folder() {
    if [ -z "$1" ] || [ -z "$2" ]; then
        echo "Usage: assistant-upload-folder <folder_path> <assistant_id> [pattern]"
        return 1
    fi
    poetry run assistant-manager upload-folder "$1" --assistant-id "$2" ${3:+--pattern "$3"}
}

# Function to generate tips
tip() {
    if [ -z "$1" ] || [ -z "$2" ]; then
        echo "Usage: tip <topic> <assistant_id>"
        return 1
    fi
    poetry run assistant-manager generate-tip "$1" --assistant-id "$2"
}
```

## Development

1. Create a new Poetry environment:
```bash
poetry shell
```

2. Run tests:
```bash
poetry run pytest
```

3. Format code:
```bash
poetry run black .
```

## Error Handling

- The tool will report any errors during file uploads or vector store operations
- For folder uploads, it will continue processing remaining files if one fails
- Invalid assistant IDs, vector store IDs, or API keys will result in clear error messages
- Files are automatically added to the correct vector store associated with each assistant

## Architecture

The tool uses OpenAI's vector store system to manage file embeddings and search capabilities:
- Each assistant is associated with a dedicated vector store
- Files are uploaded to OpenAI and then added to the appropriate vector store
- The assistant's file search tool is automatically configured to use the correct vector store
- Vector stores can be managed independently if needed

## License

MIT

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Submit a pull request