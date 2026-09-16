from src.extraction.extractor import DocumentExtractor, ExtractionError
from src.llm.llm_provider import get_llm_provider

#Импортируем модель данных
from src.models.extraction_models import ExtractionResult
from src.document.pdf_parser import parse_pdf

# Функция посмотрит LLM_PROVIDER в .env.
llm = get_llm_provider()

pdf_path = "data/input/Защита ГЩУ-ТЭЦ-3 от БПЛА  ОСНОВА.pdf"

document_ir = parse_pdf(pdf_path)


# Формируем инструкцию для модели.
# В document_text уже лежит настоящий текст из PDF.
instruction = f"""
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
"""


print("-------------------------------------------------------------------")

"""model_dump() превращает Pydantic-объект в словарь.
items() позволяет по очереди получить имя каждого поля и его значение."""

extractor = DocumentExtractor(llm)
try:
    fields = extractor.extract(
        document_ir,
        ExtractionResult,
        instruction
    )
except ExtractionError as error:
    print ("Ошибка извлечения: ",error )
    raise


print("Извлечённые данные:")
for name, field in fields.items():
    print(name, ":", field.extracted_value)

print("-------------------------------------------------------------------")

print("Нормализованные данные:")
for name, field in fields.items():
    print(name, ":", field.normalized_value)

print("-------------------------------------------------------------------")

print("Полные данные:")
for name, field in fields.items():
    print(name, ":", field)


print("-------------------------------------------------------------------")

print("Документ:", document_ir.document)
print("Первая страница:", document_ir.pages[0].page)
print("Количество блоков:", len(document_ir.pages[0].blocks))
