# openai_assistant_manager/assistant.py
import os
from pathlib import Path
from typing import Optional, List, Dict
from openai import OpenAI
from dotenv import load_dotenv
from openai.types.beta import Assistant, VectorStore
from openai.types.beta.thread_create_and_run_params import Tool, ToolResources, ToolResourcesFileSearch
from openai.types.beta.vector_stores import VectorStoreFile

load_dotenv()


class AssistantManager:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            organization=os.getenv("OPENAI_ORG_ID")
        )

    def create_vector_store(self, name: str, description: str = "") -> VectorStore:
        """Create a new vector store"""
        return self.client.beta.vector_stores.create(
            name=name
        )

    def get_vector_stores(self) -> List[VectorStore]:
        """List all vector stores"""
        return self.client.beta.vector_stores.list().data

    def get_vector_store(self, name: str) -> Optional[VectorStore]:
        """Retrieve a vector store by name"""
        vector_stores = self.get_vector_stores()
        return next((vs for vs in vector_stores if vs.name == name), None)

    def get_or_create_vector_store(self, name: str, description: str = "") -> VectorStore:
        """Get existing vector store or create new one"""
        vector_store = self.get_vector_store(name)
        if not vector_store:
            vector_store = self.create_vector_store(name, description)
        return vector_store

    def add_file_to_vector_store(self, file_id: str, vector_store_id: str) -> VectorStoreFile:
        """Add a file to a vector store"""
        return self.client.beta.vector_stores.files.create(
            vector_store_id=vector_store_id,
            file_id=file_id
        )

    def create_assistant(self, name: str, description: str, model: str) -> Assistant:
        """Create a new OpenAI assistant"""
        # Create vector store with same name as assistant
        vector_store = self.get_or_create_vector_store(name, description)

        assistant = self.client.beta.assistants.create(
            name=name,
            description=description,
            model=model,
            instructions="You are a helpful assistant that generates daily tips based on provided knowledge and topics.",
            tools=[{"type": "file_search", "file_search": {}}],
            tool_resources={
                "file_search": {
                    "vector_store_ids": [vector_store.id]
                }
            }
        )
        return assistant

    def get_existing_file_ids(self, assistant_id: str) -> List[str]:
        """Retrieve existing file IDs from an assistant"""
        assistant = self.client.beta.assistants.retrieve(assistant_id=assistant_id)
        try:
            return assistant.tool_resources.file_search.vector_store_ids
        except AttributeError:
            return []

    def upload_file(self, file_path: Path, assistant_id: str) -> str:
        """Upload a file to an assistant's knowledge base"""
        # Get assistant to find its vector store
        assistant = self.client.beta.assistants.retrieve(assistant_id=assistant_id)
        vector_store_ids = assistant.tool_resources.file_search.vector_store_ids

        if not vector_store_ids:
            raise ValueError("No vector store found for assistant")

        # Upload file
        with open(file_path, "rb") as file:
            uploaded_file = self.client.files.create(
                file=file,
                purpose="assistants"
            )

        # Add to vector store
        self.add_file_to_vector_store(uploaded_file.id, vector_store_ids[0])

        return uploaded_file.id

    def upload_folder(self, folder_path: Path, assistant_id: str, file_pattern: str = "*.docx") -> List[
        tuple[str, str]]:
        """Upload all matching files from a folder and its subfolders"""
        uploaded_files = []

        # Convert to Path object if string
        folder_path = Path(folder_path)

        # Recursively find and upload all matching files
        for file_path in folder_path.rglob(file_pattern):
            try:
                file_id = self.upload_file(file_path, assistant_id)
                uploaded_files.append((str(file_path), file_id))
            except Exception as e:
                print(f"Error uploading {file_path}: {str(e)}")

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

        while run.status in ["queued", "in_progress"]:
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )

        messages = self.client.beta.threads.messages.list(
            thread_id=thread.id
        )

        return messages.data[0].content[0].text.value