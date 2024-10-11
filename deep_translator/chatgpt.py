__copyright__ = "Copyright (C) 2020 Nidhal Baccouri"

import os
from typing import List, Optional

from deep_translator.base import BaseTranslator
from deep_translator.constants import OPEN_AI_ENV_VAR
from deep_translator.exceptions import ApiKeyException


class ChatGptTranslator(BaseTranslator):
    """
    class that wraps functions, which use the ChatGPT
    under the hood to translate word(s)
    """

    def __init__(
        self,
        source: str = "auto",
        target: str = "english",
        api_key: Optional[str] = os.getenv(OPEN_AI_ENV_VAR, None),
        model: Optional[str] = "gpt-3.5-turbo",
        base_url: Optional[str] = None,
        system_prompt: Optional[str] = None,
        **kwargs,
    ):
        """
        @param api_key: your openai api key.
        @param source: source language
        @param target: target language
        """
        if not api_key:
            raise ApiKeyException(env_var=OPEN_AI_ENV_VAR)

        self.api_key = api_key
        self.model = model

        super().__init__(source=source, target=target, **kwargs)

    def translate(self, text: str, **kwargs) -> str:
        """
        @param text: text to translate
        @return: translated text
        """
        import openai

        openai.api_key = self.api_key
        openai.base_url = self.base_url

        prompt = f"Translate the text below into {self.target}.\n"
        prompt += f'Text: "{text}"'
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})

        messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
        )

        return response.choices[0].message.content

    def translate_file(self, path: str, **kwargs) -> str:
        return self._translate_file(path, **kwargs)

    def translate_batch(self, batch: List[str], **kwargs) -> List[str]:
        """
        @param batch: list of texts to translate
        @return: list of translations
        """
        return self._translate_batch(batch, **kwargs)
