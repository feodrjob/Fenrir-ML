import json
from src.document.pdf_parser import parse_pdf


#Название файля откуда читаем
pdf_path = "data/input/Защита ГЩУ-ТЭЦ-3 от БПЛА  ОСНОВА.pdf"

document_data = parse_pdf(pdf_path)

with open ("data/output/extracted_text.json", "w", encoding="utf-8") as file:
    json.dump( # json.dump() сохраняет Python-объект в формате JSON.
        document_data.model_dump(), #превращает Pydantic-модель обратно в обычный словарь для JSON.
        file,
        ensure_ascii=False,  # Отключаем замену русских букв на Unicode-коды.
        indent=2  # Добавляем отступы для красивого форматирования JSON.
    )
print("Текст успешно извлечен и сохранен в extracted_text.json")
