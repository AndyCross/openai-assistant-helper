# OpenAI Assistant Manager

A command-line tool for managing OpenAI assistants and generating tips using their knowledge base.

## Installation

```bash
poetry install
```

## Usage

1. Create an assistant:
```bash
poetry run python -m openai_assistant_manager create-assistant --name "Tip Generator" --description "Generates daily tips"
```

2. Upload files to the assistant:
```bash
poetry run python -m openai_assistant_manager upload-file path/to/file.pdf --assistant-id "asst_..."
```

3. Generate a tip:
```bash
poetry run python -m openai_assistant_manager generate-tip "productivity" --assistant-id "asst_..."
```

## Environment Variables

Create a `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```