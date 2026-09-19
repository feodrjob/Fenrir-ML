"""
Файл: template_analyzer.py

Назначение:
    Чтение и анализ структуры DOCX-шаблонов.

Что делает:
    - открывает DOCX;
    - читает обычные абзацы;
    - читает таблицы;
    - рекурсивно заходит во вложенные таблицы;
    - сохраняет порядок содержимого;
    - убирает технические дубли объединённых ячеек.

Важно:
    На этом этапе файл только извлекает содержимое шаблона.
    Определением смысловых полей займёмся следующим этапом.
"""

from docx import Document
#Надо чтобы отличать документ от ячейки таблицы
from docx.document import Document as DocumentObject
# Table - таблица _Cell - отдельная ячейка таблицы
from docx.table import Table,_Cell
# Абзац
from docx.text.paragraph import Paragraph
# CT_P   → абзац
# CT_Tbl → таблица
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl
from ydantic import ValidationError
from src.llm.llm_provider import LLMProvider
from src.templates.template_models import TemplateAnalysisResult



def normalize_text(text: str) -> str:
    # Убираем просто лищние пробелы и переносы
    return " ".join(text.split())

def iter_document_blocks (parent):
    """
    Возвращает абзацы и таблицы в том порядке,
    в котором они находятся внутри parent.

    parent может быть:
    - весь Word-документ;
    - отдельная ячейка таблицы.
    """

    # Если передали весь документ, берем только его основное тело
    if isinstance(parent, DocumentObject):
        parent_element = parent.element.body

    # Если передали ячейку таблицы, то работаем с XML таблицы
    elif isinstance(parent, _Cell):
        parent_element = parent._tc

    else:
        raise TypeError (
            "iter_document_blocks поддерживает только Document и _Cell"
        )

    # Проходим по XML- элементам сверху вниз
    for element in parent_element.iterchildren():

        #XML элемент является абзацем
        if isinstance(element, CT_P):
            yield Paragraph(element, parent)
        # XML элемент является таблицей
        elif isinstance (element, CT_Tbl):
            yield Table(element, parent)




def extract_container_parts(parent) -> list[str]:
    """
    Рекурсивно получает текст из контейнера.

    Контейнером может быть:
    - весь документ;
    - ячейка таблицы.

    Если внутри ячейки находится ещё одна таблица,
    функция зайдёт и в неё.
    """
    parts = []

    for block in iter_document_blocks(parent):
        # Обычный обзац
        if isinstance(block, Paragraph):
            text = normalize_text(block.text)

            if text:
                parts.append(text)

        # Таблица
        elif isinstance(block, Table):
            table_parts = extract_table_parts(block)

            parts.extend(table_parts)

    return parts


def extract_table_parts(table: Table)  -> list[str]:
    """
    Извлекает текст из таблицы.

    При этом:
    - проходит по всем строкам;
    - убирает повторения объединённых ячеек;
    - рекурсивно читает содержимое каждой ячейки.
    """

    parts = []

    # Объединенная яческа модет вернуться нескольлко раз, так что помним уже обработанные ячейки
    seen_cells = set()

    for row in table.rows:
        #Текст всех уникальных ячеек текущей строки
        row_parts = []

        for cell in row.cells:
            # Берём сам XML-элемент ячейки,
            # а не его числовой id().
            cell_xml = cell._tc

            # Если это та же самая физическая XML-ячейка
            # (например, из-за объединения ячеек Word),
            # второй раз её не обрабатываем.
            if cell_xml in seen_cells:
                continue

            seen_cells.add(cell_xml)

            #Уходим в рекурсию (ячейка в ячейке в ячейке......)

            cell_parts = extract_container_parts(cell)

            if cell_parts:
                # Для одной ячейки объединяем все найденные части

                cell_text = " ".join(cell_parts)

                row_parts.append(cell_text)

            # Ячейки одной строки делим, чтобы частично сохранить структуру
            if row_parts:
                parts.append(" | ".join(row_parts))
    return parts




def extract_template_text(template_path: str) -> str:
    """
    Полностью извлекает текст DOCX-шаблона.
    """

    # Открываем Word.
    document = Document(template_path)

    # Рекурсивно читаем всё содержимое.
    parts = extract_container_parts(document)

    # Возвращаем одну строку,
    # где каждый найденный блок расположен с новой строки.
    return "\n".join(parts)











