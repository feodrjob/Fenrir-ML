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
# Надо чтобы отличать документ от ячейки таблицы
from docx.document import Document as DocumentObject
# Table - таблица _Cell - отдельная ячейка таблицы
from docx.table import Table,_Cell
# Абзац
from docx.text.paragraph import Paragraph
# CT_P   → абзац
# CT_Tbl → таблица
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl
from pydantic import ValidationError
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

class TemplateAnalysisError:
    """
    Ошибка анализа документа.
    """
    pass


class TemplateAnalyzer:
    """
    Анализирует структуру DOCX-шаблона
    и определяет поля, которые необходимо заполнить.
    """


    def __init__(
            self,
            llm: LLMProvider
    ):
        self.llm = llm

    def analyze(
            self,
            template_path: str,
    ) -> TemplateAnalysisResult:

        """
        Анализирует DOCX-шаблон и возвращает
        структурированное описание его полей.
        """

        # Сначала читаем аппаратно сожержимое word
        template_text = extract_template_text(template_path)

        # Pydantic сам создаёт JSON Schema,
        # которой должен соответствовать ответ LLM.
        response_schema = TemplateAnalysisResult.model_json_schema()

        prompt = f"""
        Проанализируй шаблон документа.

        Определи все места документа, которые должны быть заполнены
        пользователем или информационной системой.

        ВАЖНО:
        одно место для заполнения может требовать несколько отдельных данных.

        Например, если шаблон требует:
        "наименование организации, ОГРН, ИНН, адрес"

        это один блок шаблона, но четыре отдельных значения:
        - organization_name;
        - ogrn;
        - inn;
        - address.

        Для каждого места заполнения:

        1. Создай уникальный key в формате snake_case.

        2. В label сохрани текст шаблона,
           относящийся к этому месту.

        3. В description используй пояснение самого шаблона,
           особенно текст в скобках.

        4. В required_data перечисли ВСЕ отдельные значения,
           которые требуются для заполнения этого места.

        5. Каждый элемент required_data должен описывать
           одно атомарное значение.

        6. Не объединяй разные реквизиты организации,
           человека, документа, даты или материала
           в одно значение.

        7. Не придумывай требований,
           которых нет в исходном шаблоне.

        8. Не считай обычные заголовки документа полями.

        9. Не пропускай поля только потому,
           что они расположены в начале или конце документа.

        Определи тип документа,
        если он явно указан в шаблоне.

        Текст шаблона:

        {template_text}
        """

        answer = self.llm.generate(
            prompt,
            response_schema
        )

        if not answer or not answer.strip():
            raise TemplateAnalysisError (
                "LLM вернула пустой результат анализа шаблона"
            )

        try:
            return TemplateAnalysisResult.model_validate_json(answer)

        except ValidationError as error:
            raise TemplateAnalysisError(
                "LLM вернула результат, который "
                "не соответствует структуре TemplateAnalysisResult."
            ) from error

    def review(
            self,
            template_path: str,
            analysis: TemplateAnalysisResult
    ) -> TemplateAnalysisResult:
        """
        Повторно проверяет результат анализа шаблона.

        Задача второго прохода:
        - найти пропущенные поля;
        - проверить атомарность required_data;
        - убрать данные, которых шаблон напрямую не требует.
        """

        template_text = extract_template_text(template_path)

        response_schema = TemplateAnalysisResult.model_json_schema()

        current_analysis = analysis.model_dump_json(
            indent=2,
            ensure_ascii=False
        )

        prompt = f"""
    Проверь ранее выполненный анализ шаблона документа.

    У тебя есть:
    1. полный текст исходного шаблона;
    2. уже найденные поля.

    Нужно вернуть исправленный и полный результат анализа.

    Правила проверки:

    - найди места для заполнения, которые были пропущены;
    - проверь весь документ от начала до конца;
    - каждый явно требуемый реквизит должен быть отражён;
    - одно required_data должно описывать только одно атомарное значение;
    - если одно required_data содержит несколько независимых реквизитов,
      раздели его на несколько;
    - не добавляй служебные или вычисляемые данные,
      если сам шаблон их не требует;
    - не удаляй корректно найденные поля;
    - не придумывай требования, которых нет в шаблоне;
    - итог должен полностью описывать данные,
      необходимые для заполнения шаблона.

    Текст шаблона:

    {template_text}

    Текущий результат анализа:

    {current_analysis}
    """

        answer = self.llm.generate(
            prompt,
            response_schema
        )

        if not answer or not answer.strip():
            raise TemplateAnalysisError(
                "LLM вернула пустой результат проверки шаблона."
            )

        try:
            return TemplateAnalysisResult.model_validate_json(answer)

        except ValidationError as error:
            raise TemplateAnalysisError(
                "Результат проверки шаблона "
                "не соответствует TemplateAnalysisResult."
            ) from error












