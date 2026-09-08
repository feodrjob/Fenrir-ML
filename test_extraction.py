# Импортируем НАШУ функцию из файла ollama_client.py.
# То есть код подключения к Ollama второй раз не пишем.
from statistics import quantiles

from llm_provider import get_llm_provider
#Библиотека данная умеет превращать json текст в настоящйи словарь
import json
#Импортируем модель данных
from extraction_models import ExtractionResult, ExtractedField, SourceInfo
from provenance import find_source
from document_models import DocumentIR

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


"""Читаем JSON, который создал main.py.
json.load() превращает содержимое JSON-файла в обычный Python-словарь."""
with open("extracted_text.json","r", encoding="utf-8") as file:
    document_data = json.load(file)

# Проверяем, что extracted_document.json соответствует структуре нашего Document IR.
document_ir = DocumentIR.model_validate(document_data)

text = ""

for page_data in document_data["pages"]:
    text += f"\n--- СТРАНИЦА {page_data['page']} ---\n"
    text += page_data["text"]


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

{text}
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

# Одним вызовом получаем всю информацию об источнике шифра проекта.
project_code_source = find_source(
    data.project_code,
    document_data["pages"]
)

project_code_field = ExtractedField(
    normalized_value=data.project_code,
    source=SourceInfo(
        document=document_data["document"],
        page=project_code_source["page"],
        fragment=project_code_source["fragment"],
        bbox=project_code_source["bbox"]
    )
)

#Автоматически ищем страницу материала и колличества
material_source = find_source(
    data.material,
    document_data["pages"]
)

material_field = ExtractedField(
    normalized_value = data.material,
    source = SourceInfo(
        document = document_data["document"],
        page = material_source["page"],
        fragment = material_source["fragment"],
        bbox = material_source["bbox"]
    )
)

quantity_source = find_source(
    data.quantity,
    document_data["pages"]
)

quantity_field = ExtractedField(
    normalized_value = data.quantity,
    source = SourceInfo(
        document = document_data["document"],
        page = quantity_source["page"],
        fragment = quantity_source["fragment"],
        bbox = quantity_source["bbox"]
    )
)

thickness_source = find_source(
    data.thickness,
    document_data["pages"]
)

thickness_field = ExtractedField(
    normalized_value = data.thickness,
    source = SourceInfo(
        document = document_data["document"],
        page = thickness_source["page"],
        fragment = thickness_source["fragment"],
        bbox = thickness_source["bbox"]
    )
)

print("Шифр:", project_code_field)
print("Материал:", material_field)
print("Количество:", quantity_field)
print("Толщина:", thickness_field)
print("-------------------------------------------------------------------")

print("Документ:", document_ir.document)
print("Первая страница:", document_ir.pages[0].page)
print("Количество блоков:", len(document_ir.pages[0].blocks))
