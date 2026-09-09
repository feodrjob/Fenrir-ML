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

# Pydantic сам создаёт JSON Schema из нашей модели ExtractionResult.
extraction_schema = ExtractionResult.model_json_schema()


"""Читаем JSON, который создал main.py.
json.load() превращает содержимое JSON-файла в обычный Python-словарь."""
with open("extracted_text.json","r", encoding="utf-8") as file:
    document_data = json.load(file)

# Проверяем, что extracted_document.json соответствует структуре нашего Document IR.
document_ir = DocumentIR.model_validate(document_data)

text = ""
# собираем текст для LLM уже из валидированного DocumentIR

for page_data in document_ir.pages:
    text += f"\n--- СТРАНИЦА  {page_data.page} ---\n"
    text += page_data.text


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
print("-------------------------------------------------------------------")

"""model_dump() превращает Pydantic-объект в словарь.
items() позволяет по очереди получить имя каждого поля и его значение."""

extracted_fields = {}

for field_name, field_value in data.model_dump().items():
    source_data = find_source(
        field_value,
        document_ir.pages
    )

    extracted_fields[field_name] = ExtractedField(
        field_name=field_name,
        normalized_value=field_value,
        source=SourceInfo(
            document=document_ir.document,
            page=source_data["page"],
            fragment=source_data["fragment"],
            bbox=source_data["bbox"]
        )
    )


for field_name, field_data in extracted_fields.items():
    print(field_name, ":", field_data)



print("-------------------------------------------------------------------")

print("Документ:", document_ir.document)
print("Первая страница:", document_ir.pages[0].page)
print("Количество блоков:", len(document_ir.pages[0].blocks))
