# openai_assistant_manager/assistant.py
import os
from pathlib import Path
from typing import Optional, List
from openai import OpenAI
from dotenv import load_dotenv
from openai.types.beta import Assistant, FileSearchToolParam
from openai.types.beta.thread_create_and_run_params import Tool, ToolResources, ToolResourcesFileSearch

load_dotenv()


class AssistantManager:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"),
                             organization=os.getenv("OPENAI_ORG_ID"),
                             project=os.getenv("OPENAI_PROJECT_ID")
        )

    def create_assistant(self, name: str, description: str, model: str) -> Assistant:
        """Create a new OpenAI assistant"""
        assistant = self.client.beta.assistants.create(
            name=name,
            description=description,
            model=model,
            instructions="You are a helpful assistant that generates daily tips based on provided knowledge and topics."
        )
        return assistant

    def get_existing_file_ids(self, assistant_id: str) -> List[str]:
        """Retrieve existing file IDs from an assistant"""
        assistant = self.client.beta.assistants.retrieve(assistant_id=assistant_id)
        try:
            return assistant.tool_resources.get('file_search', {}).get('file_ids', [])
        except AttributeError:
            return []

    def update_assistant_files(self, assistant_id: str, file_ids: List[str]) -> None:
        """Update assistant with new file IDs while preserving file_search tool"""
        self.client.beta.assistants.update(
            assistant_id=assistant_id,
            tools=[Tool(type="file_search")],
            tool_resources=ToolResources(
                file_search=ToolResourcesFileSearch(vector_store_ids=file_ids)
            )
        )

    def upload_file(self, file_path: Path, assistant_id: str) -> str:
        """Upload a file to an assistant's knowledge base and add it to existing files"""
        # First get existing file IDs
        existing_file_ids = self.get_existing_file_ids(assistant_id)

        # Upload new file
        with open(file_path, "rb") as file:
            uploaded_file = self.client.files.create(
                file=file,
                purpose="assistants"
            )

        # Update assistant with combined file IDs
        self.update_assistant_files(
            assistant_id=assistant_id,
            file_ids=[*existing_file_ids, uploaded_file.id]
        )

        return uploaded_file.id

    def upload_folder(self, folder_path: Path, assistant_id: str, file_pattern: str = "*.docx") -> List[
        tuple[str, str]]:
        """Upload all matching files from a folder and its subfolders"""
        uploaded_files = []
        existing_file_ids = self.get_existing_file_ids(assistant_id)
        new_file_ids = []

        # Convert to Path object if string
        folder_path = Path(folder_path)

        # Recursively find and upload all matching files
        for file_path in folder_path.rglob(file_pattern):
            try:
                # Upload the file
                with open(file_path, "rb") as file:
                    uploaded_file = self.client.files.create(
                        file=file,
                        purpose="assistants"
                    )

                new_file_ids.append(uploaded_file.id)
                uploaded_files.append((str(file_path), uploaded_file.id))
            except Exception as e:
                print(f"Error uploading {file_path}: {str(e)}")

        # Update assistant once with all new files
        if new_file_ids:
            self.update_assistant_files(
                assistant_id=assistant_id,
                file_ids=[*existing_file_ids, *new_file_ids]
            )

        return uploaded_files

    def generate_tip(self, topic: str, assistant_id: str, max_tokens: int = 150) -> str:
        """Generate a tip using the assistant"""
        thread = self.client.beta.threads.create()

        message = self.client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=f"Generate a helpful tip about {topic}. Be concise and practical."
        )

        run = self.client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id
        )

        # Wait for completion
        while run.status in ["queued", "in_progress"]:
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )

        messages = self.client.beta.threads.messages.list(
            thread_id=thread.id
        )

        return messages.data[0].content[0].text.value