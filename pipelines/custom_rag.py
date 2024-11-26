"""
title: Haystack Pipeline
author: open-webui
date: 2024-05-30
version: 1.0
license: MIT
description: A pipeline for retrieving relevant information from a knowledge base using the Haystack library.
requirements: haystack-ai, datasets>=2.6.1, sentence-transformers>=2.2.0
"""

from typing import AsyncIterator, List, Union, Generator, Iterator
from schemas import OpenAIChatMessage
import httpx
import os
import asyncio
import json
from pydantic import BaseModel

URL = "http://localhost:8082/{method}/"

class Pipeline:
    class Valves(BaseModel):
        pass

    def __init__(self):
        self.url = URL
        self.name = "RAGondin"


    async def on_startup(self):
        pass


    async def on_shutdown(self):
        # This function is called when the server is stopped.
        pass

    async def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator, AsyncIterator]:
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }

        history = messages[:-1] # exclude the latest message   
        params = {
            "new_user_input": user_message
        }

        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
            async with client.stream(
                'POST',
                self.url.format(method='generate'), 
                params=params,
                headers=headers,
                json=history,
            ) as response:
                async for chunk in response.aiter_bytes():
                    yield chunk.decode()         