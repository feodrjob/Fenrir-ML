"""
Файл: aosr_context.py

Назначение:
    Подготовка данных для заполнения шаблона АОСР.

Что делает:
    - получает извлечённые поля документа;
    - преобразует их в context для Word-шаблона;
    - объединяет связанные значения в текстовые поля АОСР.

Зависимости:
    - ExtractedField
"""

from src.models.extraction_models import ExtractedField

def build_aosr_context(
        fields: dict[str, ExtractedField]
) -> dict:
    """
    Формирует context для шаблона АОСР.
    """
    project_code = fields["project_code"].normalized_value
    material = fields["material"].normalized_value
    thickness = fields["thickness"].normalized_value

    material_description = ""

    if material :
        material_description = material

    if thickness :
        material_description += f", толщина {thickness}"

    context = {
        "project_code": project_code,
        "material_description": material_description,
        #Пока такого поляне нет
        "work_description": ""
    }
    return context
