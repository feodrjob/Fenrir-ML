"""
Файл: template_slot_detector.py

Назначение:
    Детерминированный поиск мест для заполнения
    внутри DOCX-шаблона.

Что делает:
    - читает таблицы Word;
    - находит пустые ячейки с нижней границей;
    - сохраняет их физическое положение;
    - собирает текстовый контекст вокруг поля.

Важно:
    Этот модуль НЕ определяет смысл поля.
    Он только находит физические места ввода.
"""

from docx import Document
from docx.oxml.ns import qn

from src.templates.template_models import TemplateSlotCandidate


def normalize_text(text: str) -> str:
    """
    Убирает лишние пробелы и переносы.
    """

    return " ".join(text.split())


def get_unique_cells(row):
    """
    Возвращает только уникальные физические ячейки строки.

    Это важно из-за объединённых ячеек Word:
    row.cells может несколько раз вернуть одну и ту же
    XML-ячейку.
    """

    cells = []
    seen_cells = set()

    for cell in row.cells:

        cell_xml = cell._tc

        if cell_xml in seen_cells:
            continue

        seen_cells.add(cell_xml)
        cells.append(cell)

    return cells


def get_bottom_border(cell) -> str | None:
    """
    Возвращает тип нижней границы ячейки.

    Например:
        single
        nil
        None
    """

    properties = cell._tc.tcPr

    if properties is None:
        return None

    borders = properties.find(qn("w:tcBorders"))

    if borders is None:
        return None

    bottom_border = borders.find(qn("w:bottom"))

    if bottom_border is None:
        return None

    return bottom_border.get(qn("w:val"))


def is_fill_cell(cell) -> bool:
    """
    Проверяет, похожа ли ячейка на место для заполнения.

    Сейчас критерии очень простые:

    1. ячейка пустая;
    2. у неё есть видимая нижняя граница.
    """

    text = normalize_text(cell.text)

    if text:
        return False

    bottom_border = get_bottom_border(cell)

    if bottom_border is None:
        return False

    if bottom_border in ("nil", "none"):
        return False

    return True


def get_row_text(row) -> str:
    """
    Собирает весь непустой текст строки.
    """

    parts = []

    for cell in get_unique_cells(row):

        text = normalize_text(cell.text)

        if text:
            parts.append(text)

    return " | ".join(parts)


def find_previous_text(table, row_index: int) -> str | None:
    """
    Ищет ближайшую непустую строку выше.
    """

    for index in range(row_index - 1, -1, -1):

        text = get_row_text(table.rows[index])

        if text:
            return text

    return None


def find_next_text(table, row_index: int) -> str | None:
    """
    Ищет ближайшую непустую строку ниже.
    """

    for index in range(row_index + 1, len(table.rows)):

        text = get_row_text(table.rows[index])

        if text:
            return text

    return None


def get_grid_span(cell) -> int:
    """
    Определяет, сколько колонок таблицы занимает ячейка.
    """

    properties = cell._tc.tcPr

    if properties is None:
        return 1

    grid_span = properties.gridSpan

    if grid_span is None:
        return 1

    return grid_span.val


def detect_template_slots(
        template_path: str
) -> list[TemplateSlotCandidate]:
    """
    Находит все физические места заполнения
    в DOCX-шаблоне.
    """

    document = Document(template_path)

    slots = []

    for table_index, table in enumerate(document.tables):

        for row_index, row in enumerate(table.rows):

            unique_cells = get_unique_cells(row)

            for cell_index, cell in enumerate(unique_cells):

                if not is_fill_cell(cell):
                    continue

                slot = TemplateSlotCandidate(
                    table_index=table_index,
                    row_index=row_index,
                    cell_index=cell_index,
                    grid_span=get_grid_span(cell),
                    row_text=get_row_text(row) or None,
                    previous_text=find_previous_text(
                        table,
                        row_index
                    ),
                    next_text=find_next_text(
                        table,
                        row_index
                    )
                )

                slots.append(slot)

    return slots