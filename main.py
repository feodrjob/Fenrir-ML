import pymupdf
import json

#Название файля откуда читаем
pdf_path = "Защита ГЩУ-ТЭЦ-3 от БПЛА  ОСНОВА.pdf"

#Открываем документ (закроется сам при выходе из with)
with pymupdf.open(pdf_path) as doc:
    #итаем 1ю и 3ю страницы (там нужная информация)
    page_1 = doc[0]
    text_page_1 = page_1.get_text() # Вытаскиваем весь текст со страницы
    # Получаем текст страницы уже не одной строкой, а отдельными текстовыми блоками.
    raw_blocks_page_1 = page_1.get_text("blocks")

    page_3 = doc[2]
    text_page_3 = page_3.get_text()
    raw_blocks_page_3 = page_3.get_text("blocks")


def convert_blocks(raw_blocks):
    """Превращает блоки PyMuPDF в удобные словари, которые можно сохранить в JSON."""
    blocks = []

    for block in raw_blocks:
        blocks.append({
            "text": block[4].strip(),
            "bbox": [
                block[0],
                block[1],
                block[2],
                block[3]
            ]
        })
    return blocks


"""Создаём словарь, где сохраняем не только текст,
но и имя документа и номер каждой страницы."""


document_data = {
    "document": pdf_path,
    "pages": [
        {
            "page": 1,
            "text": text_page_1,
            "blocks": convert_blocks(raw_blocks_page_1)
        },
        {
            "page": 3,
            "text": text_page_3,
            "blocks": convert_blocks(raw_blocks_page_3)
        }
    ]
}
#Сохраняем результат в текстовый файл

with open ("extracted_text.txt", "w", encoding="utf-8") as file:
    file.write("--- СТРАНИЦА 1 ---\n")
    file.write(text_page_1)
    file.write("\n\n--- СТРАНИЦА 3 ---\n")
    file.write(text_page_3)

print("Текст успешно извлечен и сохранен в extracted_text.txt")

with open ("extracted_text.json", "w", encoding="utf-8") as file:
    json.dump(
        document_data,
        file,
        ensure_ascii=False,
        indent=2
    )
print("Текст успешно извлечен и сохранен в extracted_text.json")
