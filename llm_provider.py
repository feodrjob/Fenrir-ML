import os
from abc import ABC, abstractmethod

import requests
from dotenv import load_dotenv

from gigachat import GigaChat
from gigachat.models import (
    ChatCompletionRequest,
    ChatMessage,
    ChatModelOptions,
    ChatResponseFormat
)

from test_ollama_connection import response

#Загрзилил настройки из .env
load_dotenv()

#Общйи конктрак для всех LLM

class LLMProvider(ABC):
    """
    Любой провайдер обязан уметь:
    получить prompt + JSON Schema
    и вернуть строку с ответом модели.
    """

    @abstractmethod
    def generate(self, prompt, response_schema = None):
        pass


#----------------------------------------------------------------
#Настройка для Ollama
class OllamaProvider(LLMProvider):
    def __init__(self):
        #Берем настройки из .env иначе используем данные по умолчанию
        self.url = os.getenv(
            'OLLAMA_URL',
            "http://localhost:11434/api/generate"
        )

        self.model = os.getenv(
            'OLLAMA_MODEL',
            "qwen3.5:9b-q4_K_M"
        )

    def generate(self, prompt, response_schema = None):
        # Формируем запрос для Ollama
        payload = {
            "model": self.model,
            "prompt": prompt,

            #Получаем ответ целиком
            "stream": False,

            #Отключаем длинный thinking
            "options":{
                "temperature": 0
            }
        }

        #Если нам передаи schema заставляем ollama соблюдать ее
        if response_schema is not None:
            payload["format"] = response_schema
        print(f"Использую Ollama: {self.model}")

        #Отправляем запрос локальной Ollama
        response = requests.post(
            self.url,
            json=payload,
            timeout=300
        )

        #Если сервер вернул ошибку - питоне не будет дальше работать
        response.raise_for_status()

        data = response.json()

        return data["response"]

#-------------------------------------------------------------------------------
# Настраиваем Гигачат
class GigachatProvider(LLMProvider):
    #Название модели тоже берем из .env
    def __init__(self):

        self.model = os.getenv(
            "GIGACHAT_MODEL",
            "GigaChat-2"
        )

        self.ca_bundle = os.getenv(
            "GIGACHAT_CA_BUNDLE",
            "russian_trusted_root_ca_pem.crt"
        )