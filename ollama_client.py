import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen3.5:9b-q4_K_M"


def ask_ollama(prompt):
    """Отправляем запрос локальной модели и возвращаем ответ."""

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,

        # Ждём готовый ответ целиком
        "stream": False,

        # Для извлечения данных нам пока не нужны
        # длинные внутренние рассуждения модели
        "think": False
    }

    print("Отправляю запрос в Ollama...")

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=300
    )

    print("Ollama ответила!")

    # Если сервер вернул ошибку — покажем её
    response.raise_for_status()

    data = response.json()

    return data["response"]


if __name__ == "__main__":
    answer = ask_ollama(
        "Ответь только одним словом: работаешь?"
    )

    print("Ответ модели:")
    print(answer)