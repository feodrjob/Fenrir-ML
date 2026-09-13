"""
Название файла: pdf_parser.py

Назначение:
    Отвечает за извлечение информации из PDF-документов.
    Использует PyMuPDF для получения текста и координат блоков.

Основные функции:
    convert_blocks()
        Преобразует сырые блоки PyMuPDF в удобный формат.

    parse_pdf()
        Открывает PDF, извлекает страницы, текст и bbox блоков.

Зависимости:
    pymupdf
"""


import pymupdf
from src.models.document_models import DocumentIR, DocumentPage, TextBlock


def convert_blocks(raw_blocks):
    """Превращает блоки PyMuPDF в удобные словари, которые можно сохранить в JSON."""
    blocks = []

    # enumerate() даёт нам одновременно порядковый номер блока и сам блок.
    for block_id, block in enumerate (raw_blocks):
        blocks.append({
            "block_id" : block_id,
            "text": block[4].strip(),
            "bbox": [
                block[0],
                block[1],
                block[2],
                block[3]
            ]
        })
    return blocks

def parse_pdf(pdf_path):
    """
     Открывает PDF и извлекает данные документа.

     Возвращает:
         словарь с названием документа,
         страницами,
         текстом и блоками.
     """
    pages = []

    with pymupdf.open(pdf_path) as document:

        #Пока не все страницы позже заменить на автоматический проход по всему документу
        for page_number in [0,2]:

            page = document[page_number]
            blocks = []
            for block in convert_blocks(page.get_text("blocks")):
                blocks.append(
                    TextBlock(
                        block_id = block["block_id"],
                        text = block["text"],
                        bbox = block["bbox"],
                    )
                )
            pages.append(
                DocumentPage(
                    page = page_number + 1,
                    text = page.get_text("text"),
                    blocks = blocks
                )
            )
    return DocumentIR(
        document = pdf_path,
        pages = pages
    )

