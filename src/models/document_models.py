"""
Файл: document_models.py

Назначение:
    Описание внутренней структуры документа.

Что хранит:
    - страницы документа;
    - текстовые блоки;
    - координаты блоков.

Основные модели:

    TextBlock
        Один кусок текста PDF вместе с координатами.

    DocumentPage
        Одна страница документа.

    DocumentIR
        Полное внутреннее представление документа.
"""


from pydantic import BaseModel

class TextBlock(BaseModel):
    """Один текстовый блок страницы вместе с его координатами."""
    #ID лока с текстом внутри страницы
    block_id: int
    text: str
    bbox: list[float]


class DocumentPage(BaseModel):
    """Одна страница документа."""

    page: int
    text: str
    blocks: list[TextBlock]


class DocumentIR(BaseModel):
    """Внутреннее структурированное представление документа."""

    document: str
    pages: list[DocumentPage]