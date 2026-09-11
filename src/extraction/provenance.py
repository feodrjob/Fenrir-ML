from src.models.extraction_models import SourceInfo


def normalize_text(text):
    """Приводит текст к более удобному виду для сравнения."""

    #Приводим все к нижнему регистру
    text = text.lower()

    # ² и обычная 2 должны считаться одинаковыми.
    text = text.replace("²", "2")

    # Убираем пробелы, переносы строк и табы.
    text = "".join(text.split())
    return text

def find_source(value, document_ir):
    """Находит источник значения и возвращает готовый SourceInfo."""
    if value is None:
        return SourceInfo(
            document = document_ir.document,
            page = None,
            block_id = None,
            fragment = None,
            bbox = None
        )

    normalized_value = normalize_text(value)

    for page_data in document_ir.pages:
        for block in page_data.blocks:
            normalized_block_text = normalize_text(block.text)

            if normalized_value in normalized_block_text:
                fragment = None

                # Ищем конкретную строку внутри найденного текстового блока
                for line in block.text.splitlines():
                    if normalized_value in normalize_text(line):
                        fragment = line.strip()
                        break
                return SourceInfo(
                    document = document_ir.document,
                    page = page_data.page,
                    block_id = block.block_id,
                    fragment = fragment,
                    bbox = block.bbox
                )
    return SourceInfo(
        document = None,
        page = None,
        block_id = None,
        fragment = None,
        bbox = None
    )





