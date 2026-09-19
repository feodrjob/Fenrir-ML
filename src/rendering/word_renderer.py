"""
Файл: word_renderer.py

Назначение:
    Генерация DOCX-документов на основе Word-шаблонов.

Что делает:
    - открывает DOCX-шаблон;
    - получает данные для заполнения;
    - подставляет значения в placeholders;
    - сохраняет новый DOCX.

Зависимости:
    - docxtpl
"""

from docxtpl import DocxTemplate

class WordRenderer:
    """
    Сервис генерации Word-документов по DOCX-шаблону.
    """

    def render(
            self,
            template_path: str,
            output_path: str,
            context: dict
    )-> None:
        """
        Заполняет DOCX-шаблон переданными данными
        и сохраняет новый документ.
        """

        # Открываем шаблон
        template = DocxTemplate(template_path)
        # Берем словарь и ищем например код проекта (обозначние) и меняем на то что надо
        template.render(context)
        #Сохранили
        template.save(output_path)