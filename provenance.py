def normalize_text(text):
    """Приводит текст к более удобному виду для сравнения."""

    #Приводим все к нижнему регистру
    text = text.lower()

    # ² и обычная 2 должны считаться одинаковыми.
    text = text.replace("²", "2")

    # Убираем пробелы, переносы строк и табы.
    text = "".join(text.split())
    return text

def find_source(value, pages):
    """За один проход находит страницу, исходный фрагмент и bbox значения."""

    if value is None:
        return {
            "page": None,
            "fragment": None,
            "bbox": None
        }

    normalized_value = normalize_text(value)

    for page_data in pages:
        for block in page_data.blocks:
            normalized_block_text = normalize_text(block.text)

            if normalized_value in normalized_block_text:
                fragment = None

                # Ищем конкретную строку внутри найденного текстового блока
                for line in block.text.splitlines():
                    if normalized_value in normalize_text(line):
                        fragment = line.strip()
                        break
                return {
                    "page": page_data.page,
                    "fragment": fragment,
                    "bbox": block.bbox # Pydantic-объекты
                }
    return {
        "page": None,
        "fragment": None,
        "bbox": None
    }





