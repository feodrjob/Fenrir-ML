
import re
import unicodedata
from lxml.builder import unicode


def normalize_value(field_name, value):
    """Приводит извлечённое LLM значение к единому формату системы."""

    if value is None:
        return None

    # NFKC приводит разные Unicode-варианты символов к совместимому виду.
    value = unicodedata.normalize('NFKC', value)

    # Убираем лишние пробелы, табы и переносы строк.
    value = " ".join(value.split())

    # Приводим варианты "м 2", "м2" и "м²" к одному виду "м²".
    value = re.sub(r"\bм\s*2\b", "м²", value, flags=re.IGNORECASE)

    # Для толщины слово "толщина" является названием характеристики, а не её значением.
    if field_name == "thickness":
        value = re.sub(
            r"^толщина\s*",
            "",
            value,
            flags=re.IGNORECASE
        )
    return value

