import requests

print("1. Python запустился")

# Проверяем, отвечает ли локальный сервер Ollama
response = requests.get("http://localhost:11434/api/tags", timeout=10)

print("2. Ollama ответила")
print("Статус:", response.status_code)
print(response.text)