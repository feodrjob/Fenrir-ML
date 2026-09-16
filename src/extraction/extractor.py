"""
Файл: extractor.py

Назначение:
    Основной сервис извлечения информации из документов.

Что делает:
    - получает DocumentIR;
    - отправляет текст документа в LLM;
    - получает структурированный ответ;
    - ищет источник каждого значения;
    - нормализует значения;
    - возвращает словарь извлечённых фактов.

Основной класс:

    DocumentExtractor

Основной метод:

    extract()

        Выполняет полный pipeline извлечения.

Зависимости:
    - llm_provider
    - provenance
    - normalization
    - extraction_models
"""

from src.models.extraction_models import ExtractedField, FieldStatus
from src.normalization.normalization import normalize_value
from src.extraction.provenance import find_source
from pydantic import BaseModel, ValidationError
from src.models.document_models import DocumentIR
from src.llm.llm_provider import LLMProvider


class ExtractionError(Exception):
    """
      Ошибка, возникшая во время извлечения данных из документа.
    """
    pass



class DocumentExtractor:

    """
    Сервис извлечения данных из документа
    """

    def __init__(
            self,
            llm: LLMProvider
    ): # Конструктор класса
        """
        Сохраняем выбранный LLM-провайдер.
        """

        self.llm = llm


    def _build_document_text( # с _ потому что внутренний метод класса, снаружи его обычно напрямую не вызывают.
            self,
            document_ir: DocumentIR
    ) -> str:

        text = ""

        for page_data in document_ir.pages :
            text += f"\nСТРАНИЦА {page_data.page} ---\n"
            text += page_data.text

        return text

    def _build_prompt (
            self,
            document_text: str,
            instruction: str
    ) -> str:
        return f"""
        {instruction}
        
        Текст документа:
        
        {document_text}
    """

    def _build_extracted_fields(
            self,
            data: BaseModel,
            document_ir: DocumentIR
    ) -> dict[str, ExtractedField]:
        """
        Преобразует проверенный ответ LLM
        в словарь ExtractedField.
        """
        extracted_fields = {}

        for field_name, field_value in data.model_dump().items():
            source = find_source(
                field_value,
                document_ir
            )

            if field_value is None:
                status = FieldStatus.MISSING
            elif source.page is not None:
                status = FieldStatus.SOURCE_VERIFIED
            else:
                status = FieldStatus.NEEDS_REVIEW



            normalized = normalize_value(
                field_name,
                field_value
            )

            extracted_fields[field_name] = ExtractedField(
                field_name=field_name,
                extracted_value=field_value,
                normalized_value=normalized,
                source=source,
                status=status
            )
        return extracted_fields


    def extract(
            self,
            document_ir: DocumentIR, #→ ожидаем наш разобранный документ
            extraction_model: type[BaseModel], #→ ожидаем класс Pydantic-модели, например ExtractionResult
            instruction: str # → обычная текстовая инструкция
    ) -> dict[str, ExtractedField]: #→ метод возвращает словарь извлечённых полей
        """
        Извлекает данные из документа.

        Возвращает:
            словарь ExtractedField.
        """
        document_text = self._build_document_text(document_ir)
        prompt = self._build_prompt(
            document_text,
            instruction
        )

        extraction_schema =extraction_model.model_json_schema()

        # Передаём подготовленный текст документа в выбранную LLM
        answer = self.llm.generate(
            prompt,
            extraction_schema
        )

        # Проверка на то что модель хоть что-то вернула
        if not answer or not answer.strip():
            raise ExtractionError(
                "LLM вернула пустой ответ"
            )

        # Проверяем, что ответ соответствует переданной Pydantic-модели.
        try:
            data = extraction_model.model_validate_json(answer)

        except ValidationError as error:
            raise ExtractionError(
                "LLM вернула ответ, который не соответствует ожидаемой структуре."
            ) from error



        return self._build_extracted_fields(
            data,
            document_ir
        )
