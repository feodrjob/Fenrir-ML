"""
Файл: confidence.py

Назначение:
    Определение уровня доверия к извлечённому значению.

Что учитывает:
    - существует ли значение;
    - найден ли его источник в исходном документе;
    - прошло ли значение программную валидацию.

Важно:
    Confidence не является "уверенностью LLM".
    Это оценка, которую рассчитывает сама система
    на основе проверяемых признаков.
"""

from enum import Enum
from src.validation.field_validation import ValidationStatus

class ConfidenceLevel(str, Enum):
    """
    Уровень доверия к извлечённому значению.
    """

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

def calculate_confidence (
        value_present: bool,
        source_verified: bool,
        validation_status: ValidationStatus,
) -> ConfidenceLevel | None:
    """
    Рассчитывает уровень доверия к извлечённому значению.
    """

    #Если нет значений, то нет смысла считать
    if not value_present:
        return None

    # Если не смогли подтвердить значение исходным документом - доверие низкое
    if not source_verified:
        return ConfidenceLevel.LOW

    # Источник найден и программная проверка пройдена
    if validation_status == ValidationStatus.VALID:
        return ConfidenceLevel.HIGH

    # Есть источник, но некорректный формат
    if validation_status == ValidationStatus.INVALID:
        return ConfidenceLevel.LOW

    # Есть источник но нет программного правила проверки
    return ConfidenceLevel.MEDIUM
















