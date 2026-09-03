# Импортируем НАШУ функцию из файла ollama_client.py.
# То есть код подключения к Ollama второй раз не пишем.
from llm_provider import get_llm_provider
#Библиотека данная умеет превращать json текст в настоящйи словарь
import json
#Импортируем модель данных
from extraction_models import ExtractionResult, ExtractedField, SourceInfo


# Функция посмотрит LLM_PROVIDER в .env.
llm = get_llm_provider()

# Описываем структуру ответа,
# которую Qwen обязана вернуть.
extraction_schema = {

    # Ответ должен быть одним объектом {...}
    # Поэтому массив [...] теперь не подходит.
    "type": "object",

    # Перечисляем разрешённые поля
    "properties": {

        "project_code": {
            # Поле может быть строкой или null
            "anyOf": [
                {"type": "string"},
                {"type": "null"}
            ]
        },

        "material": {
            "anyOf": [
                {"type": "string"},
                {"type": "null"}
            ]
        },

        "quantity": {
            # Именно string не позволит вернуть число 162
            "anyOf": [
                {"type": "string"},
                {"type": "null"}
            ]
        },

        "thickness": {
            # Поэтому 0.2 как число тоже уже не пройдёт
            "anyOf": [
                {"type": "string"},
                {"type": "null"}
            ]
        }
    },

    # Эти четыре ключа должны присутствовать всегда.
    # Если данных нет — модель должна поставить null.
    "required": [
        "project_code",
        "material",
        "quantity",
        "thickness"
    ],

    # Запрещаем модели придумывать пятое,
    # шестое и другие поля.
    "additionalProperties": False
}


# Открываем текстовый файл, который ранее создал PyMuPDF
with open("extracted_text.txt","r", encoding="utf-8") as file:
    # read() читает всё содержимое файла в одну строку
    document_text = file.read()

# Ищем место, где в тексте встречается бронеплёнка
position = document_text.find ("Бронеплёнка")

# Печатаем небольшой кусок текста вокруг неё,
# чтобы увидеть, как PyMuPDF реально извлёк эти строки
print (document_text[position:position + 200])
# Формируем инструкцию для модели.
# В document_text уже лежит настоящий текст из PDF.
prompt = f"""
Извлеки данные из рабочей документации.

Найди:
- шифр рабочей документации;
- материал "Бронеплёнка противоосколочная";
- количество этой бронеплёнки;
- толщину этой бронеплёнки.

ВАЖНО:
копируй значения так, как они указаны в исходном тексте.

Не переводи единицы измерения.
Не изменяй значения.

Например:
200 мкм должно остаться "200 мкм",
а не превращаться в "0.2 мм".

Если данных нет, используй null.

Текст документа:

{document_text}
"""


# Наша уже написанная функция отправляет prompt в Ollama.

# Передаём одновременно:
# 1. наше задание
# 2. строгую структуру ответа
answer = llm.generate(
    prompt,
    extraction_schema
)

# model_validate_json() делает сразу две вещи:
#
# 1. превращает JSON-строку в данные Python;
# 2. проверяет их по правилам ExtractionResult.
#
# Если структура неправильная —
# Pydantic сразу выдаст понятную ошибку.

data = ExtractionResult.model_validate_json(answer)

#Проверим что можем обратиться к каждому значению по ключу
# У объекта Pydantic поля доступны через точку.
print("Шифр проекта:", data.project_code)
print("Материал:", data.material)
print("Количество:", data.quantity)
print("Толщина:", data.thickness)
# print("Результат извлечения")
# print (answer)

"""Пока источник создаём вручную только для проверки самой модели provenance.
Позже документ, страницу и координаты система будет определять автоматически."""

project_code_field = ExtractedField(
    value = data.project_code,

    source=SourceInfo(
        document = "Защита ГЩУ-ТЭЦ-3 от БПЛА ОСНОВА.pdf",
        page = 1
    )
)
print(project_code_field)