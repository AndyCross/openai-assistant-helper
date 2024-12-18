from atproto import Client, models
import os
from typing import Optional, List
import regex


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

    def count_graphemes(self, text: str) -> int:
        """
        Count the number of graphemes in a string using Unicode segmentation.

        Args:
            text: String to count graphemes in

        Returns:
            int: Number of graphemes
        """
        return len(regex.findall(r'\X', text))

    def chunk_text(self, text: str, max_graphemes: int = 300) -> List[str]:
        """
        Split text into chunks that respect grapheme limits and natural breaking points.

        Args:
            text: Text to split into chunks
            max_graphemes: Maximum graphemes per chunk (default: 300)

        Returns:
            List[str]: List of text chunks
        """
        # If text is already within limits, return as single chunk
        if self.count_graphemes(text) <= max_graphemes:
            return [text]

        chunks = []
        current_chunk = ""

        # Reserve space for thread numbering (e.g., "1/4 ")
        thread_number_space = 5  # Assuming max 9 parts
        effective_max = max_graphemes - thread_number_space

        # Split into sentences first
        sentences = regex.split(r'(?<=[.!?])\s+', text)

        for sentence in sentences:
            # If single sentence exceeds limit, split on commas
            if self.count_graphemes(sentence) > effective_max:
                comma_parts = sentence.split(',')
                for part in comma_parts:
                    part = part.strip()
                    if not current_chunk:
                        current_chunk = part
                    elif self.count_graphemes(f"{current_chunk}, {part}") <= effective_max:
                        current_chunk = f"{current_chunk}, {part}"
                    else:
                        chunks.append(current_chunk)
                        current_chunk = part
            else:
                if not current_chunk:
                    current_chunk = sentence
                elif self.count_graphemes(f"{current_chunk} {sentence}") <= effective_max:
                    current_chunk = f"{current_chunk} {sentence}"
                else:
                    chunks.append(current_chunk)
                    current_chunk = sentence

        if current_chunk:
            chunks.append(current_chunk)

        # Add thread numbering
        total_chunks = len(chunks)
        return [f"{i + 1}/{total_chunks} {chunk}" for i, chunk in enumerate(chunks)]

    def publish_thread(self, text: str) -> List[str]:
        """
        Publish a thread of posts to Bluesky, automatically splitting long content.

        Args:
            text: The content to post

        Returns:
            List[str]: URLs of all published posts in the thread
        """
        chunks = self.chunk_text(text)
        urls = []
        parent_uri = None
        parent_cid = None
        root_uri = None
        root_cid = None

        for chunk in chunks:
            # Prepare reply reference if this is part of a thread
            reply_ref = None
            if parent_uri and parent_cid:
                parent_ref = {"uri": parent_uri, "cid": parent_cid}
                root_ref = {"uri": root_uri or parent_uri, "cid": root_cid or parent_cid}
                reply_ref = models.AppBskyFeedPost.ReplyRef(root=root_ref, parent=parent_ref)

            response = self.client.send_post(
                text=chunk,
                reply_to=reply_ref
            )

            # Update parent and root references for the next post
            parent_uri = response.uri
            parent_cid = response.cid
            if not root_uri:
                root_uri = response.uri
                root_cid = response.cid

            post_url = f"https://bsky.app/profile/{response.uri.split('/')[-2]}/post/{response.uri.split('/')[-1]}"
            urls.append(post_url)

        return urls

    def publish_post(self, text: str) -> str:
        """
        Publish a single post to Bluesky and return its URL.
        Raises ValueError if text exceeds grapheme limit.

        Args:
            text: The content to post

        Returns:
            str: URL of the published post
        """
        if self.count_graphemes(text) > 300:
            return "\n".join(self.publish_thread(text))

        response = self.client.send_post(text=text)
        return f"https://bsky.app/profile/{response.uri.split('/')[-2]}/post/{response.uri.split('/')[-1]}"

    def get_profile(self) -> dict:
        """Get the current user's profile information"""
        return self.client.get_profile(self.identifier)

