"""
Файл: field_validation.py

Назначение:
    Программная проверка извлечённых и нормализованных значений.

Что делает:
    - получает название поля и его значение;
    - проверяет значение по детерминированным правилам;
    - сообщает результат проверки.

Важно:
    Validation не изменяет значение.
    Изменением формата занимается normalization.py.
"""


import re
from enum import Enum
from pydantic import BaseModel
from pydantic_core.core_schema import field_after_validator_function


class ValidationStatus(str, Enum):
    """
    Результат программной проверки значения.
    """

    VALID = "VALID"
    INVALID = "INVALID"
    NOT_CHECKED = "NOT_CHECKED"


class FieldValidationResult(BaseModel):
    """
    Результат проверки одного значения.
    """

    status: ValidationStatus
    reason: str | None = None

def validate_field (
        field_name: str,
        value: str | None,
) -> FieldValidationResult:
    """
    Проверяет значение конкретного поля.
    """

    # Если значения нет, проверять нечего
    if value is None:
        return FieldValidationResult(
            status = ValidationStatus.NOT_CHECKED,
            reason = "Значение отсутствует"
        )

    if field_name == "thickness":
        pattern = r"^\d+(?:[.,]\d+)?\s*(мкм|мм)$"

        if re.match(pattern,value, flags=re.IGNORECASE):
            return FieldValidationResult(
                status = ValidationStatus.VALID
            )

        return FieldValidationResult(
            status = ValidationStatus.INVALID,
            reason = "Толщина должна содержать число и единицу измерения"
        )

    if field_name == "quantity":
        pattern = r"^\d+(?:[.,]\d+)?\s*(м²|м2|м³|м3|м|шт|кг|т|л)$"

        if re.match(pattern, value, flags = re.IGNORECASE):
            return FieldValidationResult(
                status = ValidationStatus.VALID
            )
        return FieldValidationResult(
            status = ValidationStatus.INVALID,
            reason = "Количество должно содержать число и допустимую единицу измерения"
        )

    if field_name == "project_code":

        #Убираем пробелы по краям
        code = value.strip()

        if len (code) < 2 or len (code) > 50:
            return FieldValidationResult(
                status = ValidationStatus.INVALID,
                reason = "Недопустимая длина шфира"
            )
        if not any(char.isdigit() for char in code):
            return FieldValidationResult(
                status=ValidationStatus.INVALID,
                reason="Шифр документа не содержит цифр."
            )

        return FieldValidationResult(
            status = ValidationStatus.VALID
        )

    # Если для поля пока нет отдлеьного правила
    return FieldValidationResult(
        status = ValidationStatus.NOT_CHECKED,
        reason = f"Для поля '{field_name}' правило проверки пока не задано."
    )







































