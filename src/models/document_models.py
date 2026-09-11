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