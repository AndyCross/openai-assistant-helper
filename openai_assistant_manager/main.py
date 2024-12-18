# openai_assistant_manager/main.py
import typer
from pathlib import Path
from typing import Optional
from .assistant import AssistantManager
from .bluesky import BlueskyManager

app = typer.Typer()
assistant_manager = AssistantManager()
bluesky_manager = BlueskyManager()


@app.command()
def create_vector_store(
        name: str = typer.Argument(..., help="Name of the vector store"),
        description: str = typer.Option("", help="Description of the vector store")
):
    """Create a new vector store"""
    vector_store = assistant_manager.create_vector_store(name, description)
    typer.echo(f"Created vector store: {vector_store.id}")


@app.command()
def get_vector_store(
        name: str = typer.Argument(..., help="Name of the vector store")
):
    """Get a vector store by name"""
    vector_store = assistant_manager.get_vector_store(name)
    if vector_store:
        typer.echo(f"Found vector store: {vector_store.id}")
    else:
        typer.echo(f"No vector store found with name: {name}")


@app.command()
def create_assistant(
        name: str = typer.Option(..., help="Name of the assistant"),
        description: str = typer.Option(..., help="Description of the assistant"),
        model: str = typer.Option("gpt-4-1106-preview", help="Model to use")
):
    """Create a new OpenAI assistant"""
    assistant = assistant_manager.create_assistant(name, description, model)
    typer.echo(f"Created assistant: {assistant.id}")


@app.command()
def upload_file(
        file_path: Path = typer.Argument(..., help="Path to file to upload"),
        assistant_id: str = typer.Option(..., help="Assistant ID to upload to")
):
    """Upload a file to an assistant's knowledge base"""
    file_id = assistant_manager.upload_file(file_path, assistant_id)
    typer.echo(f"Uploaded file: {file_id}")


@app.command()
def upload_folder(
        folder_path: Path = typer.Argument(..., help="Path to folder to upload"),
        assistant_id: str = typer.Option(..., help="Assistant ID to upload to"),
        pattern: str = typer.Option("*.docx", help="File pattern to match (e.g., *.docx, *.pdf)")
):
    """Upload all matching files from a folder and its subfolders"""
    uploaded_files = assistant_manager.upload_folder(folder_path, assistant_id, pattern)

    if not uploaded_files:
        typer.echo(f"No matching files found in {folder_path}")
        return

    typer.echo(f"Uploaded {len(uploaded_files)} files:")
    for file_path, file_id in uploaded_files:
        typer.echo(f"- {file_path}: {file_id}")


def _generate_tip(topic: str, assistant_id: str, max_tokens: int) -> str:
    """Internal function to generate a tip"""
    return assistant_manager.generate_tip(topic, assistant_id, max_tokens)


@app.command()
def generate_tip(
        topic: str = typer.Argument(..., help="Topic for the tip"),
        assistant_id: str = typer.Option(..., help="Assistant ID to use"),
        max_tokens: int = typer.Option(150, help="Maximum length of the tip")
):
    """Generate a tip using the assistant"""
    tip = _generate_tip(topic, assistant_id, max_tokens)
    typer.echo(f"Tip: {tip}")


@app.command()
def publish_tip(
        topic: str = typer.Argument(..., help="Topic for the tip"),
        assistant_id: str = typer.Option(..., help="Assistant ID to use"),
        max_tokens: int = typer.Option(150, help="Maximum length of the tip"),
        preview: bool = typer.Option(False, help="Preview the tip without publishing")
):
    """Generate and publish a tip to Bluesky"""
    tip = _generate_tip(topic, assistant_id, max_tokens)

    if preview:
        typer.echo("Preview mode - tip would be published to Bluesky:")
        typer.echo(f"Tip: {tip}")
        return

    try:
        post_url = bluesky_manager.publish_post(tip)
        typer.echo(f"Successfully published tip to Bluesky!")
        typer.echo(f"Tip: {tip}")
        typer.echo(f"Post URL: {post_url}")
    except Exception as e:
        typer.echo(f"Error publishing to Bluesky: {str(e)}", err=True)


if __name__ == "__main__":
    app()