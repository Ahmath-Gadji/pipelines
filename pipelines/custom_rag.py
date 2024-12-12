"""
title: Haystack Pipeline
author: open-webui
date: 2024-05-30
version: 1.0
license: MIT
description: A pipeline for retrieving relevant information from a knowledge base using the Haystack library.
"""

from typing import AsyncIterator, List, Union, Generator, Iterator
import httpx
import json
import json
from urllib.parse import urlparse, quote
from pydantic import BaseModel

URL = "http://chainlit-app:8000/{method}/"

SOURCE = '\n **Sources**: \n'

class Pipeline:
    class Valves(BaseModel):
        pass

    def __init__(self):
        self.url = URL
        self.name = "RAGondin"


    async def on_startup(self):
        #async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
        #    response = await client.get(url=self.url.format(method='hello'))
        #    print(response.text)
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

        params = {
            "new_user_input": user_message
        }

        # Preprocessing
        for i, message in enumerate(messages):
            if message['role'] == 'assistant':
                message['content'] = message['content'].split(SOURCE)[0]
                # print(message)
                messages[i] = message

        history = messages[:-1] # exclude the latest message  


        print(f"url: {self.url.format(method='generate')}")
        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
            async with client.stream(
                'POST',
                self.url.format(method='generate'), 
                params=params,
                headers=headers,
                json=history,
            ) as response:
                
                metadata_sources = response.headers.get("X-Metadata-Sources")
                formatted_src = format_sources(metadata_sources)
                async for token in response.aiter_bytes():
                    yield token.decode()   

                yield formatted_src   



def format_sources(metadata_sources):
    sources = json.loads(metadata_sources)
    formatted_sources = []
    markdown_links = []
    
    if sources:
        for doc in sources:
            doc['url'] = 'https://demo-lucie.linagora.com/rag-api/static/' + doc['url'].split('static/')[1]
            print(f"doc: {doc['url']}")
            encoded_url = quote(doc['url'], safe=':/')

            parsed_url = urlparse(doc['url'])
            doc_name = parsed_url.path.split('/')[-1]

            if "pdf" in doc_name.lower():
                encoded_url = f'{encoded_url}#page={doc['page']}'

            s = f"* {doc['doc_id']} : [{doc_name}]({encoded_url})"
            s2 = f"{doc['doc_id']}: {encoded_url} '{doc_name}'"

            # s = f"* {doc['doc_id']}: {encoded_url} '{doc_name}'"
            formatted_sources.append(s)
            markdown_links.append(s2)

        return f'{SOURCE}' + '\n' + '\n'.join(markdown_links) + '\n' + '\n'.join(formatted_sources)  
    else:
        return ''