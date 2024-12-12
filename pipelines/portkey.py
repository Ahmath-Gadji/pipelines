from pydantic import BaseModel, Field
from typing import Optional, Union, Generator, Iterator, List

import os
import json
import requests


virtual_keys = {"openai":"open-ai-virtual-123456"}  # ex: {"perplexity": "tooljet-perplex-3f95ca"}

class Pipeline:
    class Valves(BaseModel):
        PORTKEY_API_BASE_URL: str = Field(
            default="https://api.portkey.ai/v1",  # Change this if using a self-hosted or enterprise solution
            description="The base URL for Portkey API endpoints. Change this if using a self-hosted or enterprise solution",
        )
        PORTKEY_API_KEY: str = Field(
            default="",
            description="Required API key to access Portkey services.",
            env = "PORTKEY_API_KEY"
        )
        CUSTOM_HOST: str = Field(
            default="",
            description="Custom OpenAI host URL",
            env = "OPENAI_API_BASE"
        )
        AUTH: str = Field(
            default="",
            description="Custom OpenAI host KEY",
            env='API_KEY'
        )
        VIRTUAL_KEY: str = Field(
            default="",
            description="Portkey virtual key"
        )       

    def __init__(self):
        #self.type = "manifold"
        self.valves = self.Valves()
        self.VIRTUAL_KEYS: dict = {"openai":self.valves.VIRTUAL_KEY}

    #def pipelines(self):
    #    # add model ids in the following format "{provider}/{model}"
    #    return [
    #        {
    #            "id": "meta/meta-llama-31-8b-it",
    #            "name": "meta/meta-llama-31-8b-it",
    #        }
    #    ]

    def pipe(self, user_message: str,body: dict,model_id: str,messages: List[dict]) -> Union[str, Generator, Iterator]:
        if not self.valves.PORTKEY_API_KEY:
            raise Exception("PORTKEY_API_KEY not provided in the valves.")
        
        from portkey_ai import Portkey

        #model_id = body["model"]
        #if model_id.startswith("portkey."):
        #    model_id = model_id[len("portkey.") :]
        #model_id_parts = model_id.split("/")
        #model_provider = model_id_parts[0]
        #model_id = model_id_parts[1]
        model_provider="openai"
        virtual_key = self.VIRTUAL_KEYS[f"{model_provider}"]
        #metadata = {"_user": f"{__user__.get('email')}"}

        print(f"messages: {messages}")
        print(f"body: {body}")
        
        portkey = Portkey(
            api_key=self.valves.PORTKEY_API_KEY,
            provider=model_provider, # This can be mistral-ai, openai, or anything else
            custom_host=self.valves.CUSTOM_HOST, # Your custom URL with version identifier
            virtual_key=virtual_key,
            Authorization= self.valves.AUTH # If you need to pass auth
        )
        #payload = {**body, "model": model_id}

        #headers = {
        #    "x-portkey-api-key": f"{self.valves.PORTKEY_API_KEY}",
        #    "Content-Type": "application/json",
        #    "accept": "application/json",
        #    "x-portkey-provider": f"{model_provider}",
        #    "x-portkey-virtual-key": f"{virtual_key}",
        #    "x-portkey-metadata": json.dumps(metadata),
        #}

        try:
            #r = requests.post(
            #    url=f"{self.valves.PORTKEY_API_BASE_URL}/chat/completions",
            #    json=payload,
            #    headers=headers,
            #    stream=True,
            #)

            completion = portkey.chat.completions.create(
                messages= messages,
                model = "meta-llama-31-8b-it",
                timeout=60,
                stream=True
            )
            for chunk in completion:
                # Extract content from the chunk if necessary
                content = chunk.choices[0].delta.content
                print(f"content: {content}")
                if content:
                    yield content            
            #print(f"completion: {completion.choices[0].message.content.strip()}")
            #return completion.choices[0].message.content.strip()
        except Exception as e:
            return f"Error: {e}"
