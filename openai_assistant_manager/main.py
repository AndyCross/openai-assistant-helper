# openai_assistant_manager/main.py
import typer
from pathlib import Path
from .assistant import AssistantManager

app = typer.Typer()
manager = AssistantManager()

@app.command()
def create_assistant(
    name: str = typer.Option(..., help="Name of the assistant"),
    description: str = typer.Option(..., help="Description of the assistant"),
    model: str = typer.Option("gpt-4-1106-preview", help="Model to use")
):
    """Create a new OpenAI assistant"""
    assistant = manager.create_assistant(name, description, model)
    typer.echo(f"Created assistant: {assistant.id}")

@app.command()
def upload_file(
    file_path: Path = typer.Argument(..., help="Path to file to upload"),
    assistant_id: str = typer.Option(..., help="Assistant ID to upload to")
):
    """Upload a file to an assistant's knowledge base"""
    file_id = manager.upload_file(file_path, assistant_id)
    typer.echo(f"Uploaded file: {file_id}")

@app.command()
def upload_folder(
        folder_path: Path = typer.Argument(..., help="Path to folder to upload"),
        assistant_id: str = typer.Option(..., help="Assistant ID to upload to"),
        pattern: str = typer.Option("*.docx", help="File pattern to match (e.g., *.docx, *.pdf)")
):
    """Upload all matching files from a folder and its subfolders"""
    uploaded_files = manager.upload_folder(folder_path, assistant_id, pattern)

    if not uploaded_files:
        typer.echo(f"No matching files found in {folder_path}")
        return

    typer.echo(f"Uploaded {len(uploaded_files)} files:")
    for file_path, file_id in uploaded_files:
        typer.echo(f"- {file_path}: {file_id}")

@app.command()
def generate_tip(
    topic: str = typer.Argument(..., help="Topic for the tip"),
    assistant_id: str = typer.Option(..., help="Assistant ID to use"),
    max_tokens: int = typer.Option(150, help="Maximum length of the tip")
):
    """Generate a tip using the assistant"""
    tip = manager.generate_tip(topic, assistant_id, max_tokens)
    typer.echo(f"Tip: {tip}")

if __name__ == "__main__":
    app()