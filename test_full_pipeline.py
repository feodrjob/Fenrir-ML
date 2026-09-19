from src.document.pdf_parser import parse_pdf
from src.extraction.extractor import DocumentExtractor
from src.llm.llm_provider import get_llm_provider
from src.models.extraction_models import ExtractionResult
from src.rendering.word_renderer import WordRenderer
from src.rendering.aosr_context import build_aosr_context

pdf_path = "data/input/Защита ГЩУ-ТЭЦ-3 от БПЛА  ОСНОВА.pdf"

document_ir = parse_pdf(pdf_path)

llm = get_llm_provider()

extractor = DocumentExtractor(llm)

instruction = """
Извлеки данные из рабочей документации.

Найди:
- шифр рабочей документации;
- название проекта или рабочей документации;
- точное наименование выполненной строительной работы;
- материал "Бронеплёнка противоосколочная";
- количество этой бронеплёнки;
- толщину этой бронеплёнки.

Правила для названия выполненной работы:
- значение должно описывать именно выполненную строительную работу;
- не используй название проекта, объекта или рабочей документации как название работы;
- не придумывай формулировку самостоятельно;
- если отдельного наименования выполненной работы в документе нет, используй null.

ВАЖНО:
копируй значения так, как они указаны в исходном тексте.

Не переводи единицы измерения.
Не изменяй значения.
Не дополняй данные своими предположениями.

Если каких-либо данных нет в документе, используй null.
"""

fields = extractor.extract(
    document_ir,
    ExtractionResult,
    instruction
)

print("Извлечённые данные:")
for name, field in fields.items():
    print(name, ":", field.normalized_value)

context = build_aosr_context(fields)
print("\nДанные для шаблона АОСР:")
for name, value in context.items():
    print(name, ":", value)

renderer = WordRenderer()

renderer.render(
    template_path="templates/aosr_344_template.docx",
    output_path="data/output/generated_aosr_from_pdf.docx",
    context=context
)

print("DOCX успешно сгенерирован из данных PDF")