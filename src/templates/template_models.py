"""
Файл: template_models.py

Назначение:
    Модели данных для результатов анализа DOCX-шаблонов.

Основные классы:
    TemplateFieldSpec
    TemplateAnalysisResult

Важно:
    Эти модели не привязаны к АОСР.
    Они должны подходить для любых будущих шаблонов.
"""

from pydantic import BaseModel

class TemplateFieldSpec(BaseModel):
    """
    Описание одного поля, которое необходимо заполнить
    в анализируемом шаблоне.
    """

    # Машиночитаемое имя поля
    key: str
    # Текст рядом с полем в самом шаблоне
    label: str
    # Подсказака из шаблона (что требуется)
    description: str | None = None


class TemplateAnalysisResult(BaseModel):
    """
    Результат анализа всего шаблона документа.
    """

    # Тип документа если его удалось определеить
    document_type: str | None = None

    # Все найденные поля шаблона
    fields: list[TemplateFieldSpec]