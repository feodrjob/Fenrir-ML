# BaseModel — базовый класс Pydantic.
# Наследуясь от него, мы получаем автоматическую
# проверку данных.

from pydantic import BaseModel

#описываем откуда было получено конкретное значение
class SourceInfo(BaseModel):

    document:str | None
    page:int | None
    fragment:str | None
    #Координаты текстового блока
    bbox: list[float] | None = None # Благодаря этому старый код не сломается, даже если bbox пока не передан.

#Одно найденное значение с информацией об источнике
class ExtractedField(BaseModel):
    #Само значение
    normalized_value:str | None

    # Откуда система взяла значение
    source: SourceInfo | None





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

