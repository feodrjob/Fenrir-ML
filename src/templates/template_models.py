"""
Файл: template_models.py

Назначение:
    Модели данных для результатов анализа DOCX-шаблонов.

Основные классы:
    TemplateDataRequirement
    TemplateFieldSpec
    TemplateAnalysisResult
"""


from pydantic import BaseModel

class TemplateDataRequirement(BaseModel):
    """
    Одно атомарное значение, которое требуется
    для заполнения поля шаблона.
    """

    key: str
    # Что именно требуется найти
    description: str



class TemplateFieldSpec(BaseModel):
    """
    Описание одного поля, которое необходимо заполнить
    в анализируемом шаблоне.
    """

    # Уникальное имя самого блока шаблона.
    key: str
    # Текст поля в исходном документе.
    label: str
    # Пояснение из шаблона.
    description: str | None = None
    # Какие отдельные данные нужны, чтобы заполнить это место.
    required_data: list[TemplateDataRequirement] = []


class TemplateAnalysisResult(BaseModel):
    """
    Результат анализа всего шаблона документа.
    """

    # Тип документа если его удалось определеить
    document_type: str | None = None

    # Все найденные поля шаблона
    fields: list[TemplateFieldSpec]



class TemplateSlotCandidate(BaseModel):
    """
    Физическое место в DOCX,
    которое похоже на область для заполнения.
    """
    #Номер таблицы
    table_index: int

    # Номер строки таблицы
    row_index: int

    # Номер ячейчки внутри строки (уникальный)
    cell_index: int

    # Сколько колонок занимает ячейка
    grid_span: int = 1

    # Текст, который находится в этой же строке.
    row_text: str | None = None

    # Ближайший текст выше.
    previous_text: str | None = None

    # Ближайший текст ниже.
    next_text: str | None = None
















