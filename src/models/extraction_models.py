# BaseModel — базовый класс Pydantic.
# Наследуясь от него, мы получаем автоматическую
# проверку данных.

from pydantic import BaseModel
from enum import Enum

#описываем откуда было получено конкретное значение
class SourceInfo(BaseModel):

    document:str | None
    page:int | None
    fragment:str | None
    block_id: int | None = None
    #Координаты текстового блока
    bbox: list[float] | None = None # Благодаря этому старый код не сломается, даже если bbox пока не передан.

class FieldStatus (str, Enum):
    MISSING = "MISSING",
    SOURCE_VERIFIED = "SOURCE_VERIFIED",
    NEEDS_REVIEW = "NEEDS_REVIEW"


class ExtractedField(BaseModel):
    """Один извлечённый факт вместе с исходным результатом LLM, нормализованным значением и источником."""

    # Название факта, например quantity или project_code.
    field_name: str

    # Значение ровно в том виде, в котором его вернула LLM.
    extracted_value: str | None

    # Значение после нашей детерминированной обработки. Пока его ещё не вычисляем.
    normalized_value: str | None = None

    # Информация о месте в исходном документе.
    source: SourceInfo | None

    # Статус
    status: FieldStatus





class ExtractionResult(BaseModel):
    """
    Описывает данные, которые мы ожидаем получить
    от LLM для нашего текущего тестового сценария.
    """

    # str | None означает:
    # значение может быть строкой ИЛИ None.
    #
    # None в Python соответствует null в JSON.

    project_code:str | None

    material:str | None

    quantity:str | None

    thickness:str | None

