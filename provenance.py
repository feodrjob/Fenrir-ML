def normalize_text(text):
    """Приводит текст к более удобному виду для сравнения."""

    #Приводим все к нижнему регистру
    text = text.lower()

    # ² и обычная 2 должны считаться одинаковыми.
    text = text.replace("²", "2")

    # Убираем пробелы, переносы строк и табы.
    text = "".join(text.split())
    return text



def find_source_page(value, pages):
    """Ищет страницу, на которой встречается найденное моделью значение."""

    # Если модель ничего не нашла возврашаем null
    if value is None:
        return None

    normalized_value = normalize_text(value)

    # По очереди перебираем страницы докумнета
    for page_data in pages:
        normalized_page_text = normalize_text(page_data["text"])
        #Проверяем встречается ли значение внутри текста страницы
        if normalized_value in normalized_page_text:
            return page_data["page"]

    return None  #Если ничего не нашли

def find_source_fragment(value, pages):
    """Ищет исходную строку текста, в которой встречается найденное значение."""
    if value is None:
        return None

    normalized_value = normalize_text(value)

    for page_data in pages:

        for line in page_data["text"].splitlines():
            if normalized_value in normalize_text(line):
                return line.strip() #убирает лишние пробелы в начале и конце строки.

    return None