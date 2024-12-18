# openai_assistant_manager/bluesky.py
from atproto import Client

import os
from typing import Optional


class BlueskyManager:
    def __init__(self, identifier: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize BlueskyManager with optional credentials.
        If not provided, will attempt to read from environment variables.
        """
        self.identifier = identifier or os.getenv("BLUESKY_IDENTIFIER")
        self.password = password or os.getenv("BLUESKY_PASSWORD")
        self._client: Optional[Client] = None

    @property
    def client(self) -> Client:
        """Lazy initialization of Bluesky client"""
        if not self._client:
            if not self.identifier or not self.password:
                raise ValueError(
                    "Bluesky credentials not provided and BLUESKY_IDENTIFIER/BLUESKY_PASSWORD environment variables not set")

            self._client = Client()
            self._client.login(self.identifier, self.password)

        return self._client

    def publish_post(self, text: str) -> str:
        """
        Publish a post to Bluesky and return its URL

        Args:
            text: The content to post

        Returns:
            str: URL of the published post
        """
        response = self.client.send_post(text=text)
        return f"https://bsky.app/profile/{response.uri.split('/')[-2]}/post/{response.uri.split('/')[-1]}"

    def get_profile(self) -> dict:
        """Get the current user's profile information"""
        return self.client.get_profile(self.identifier)