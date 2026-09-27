from src.llm.llm_provider import get_llm_provider
from src.templates.template_analyzer import TemplateAnalyzer


template_path = "templates/aosr_344_source.docx"

llm = get_llm_provider()
analyzer = TemplateAnalyzer(llm)


# -----------------------------
# Первый анализ шаблона
# -----------------------------

print("Первичный анализ шаблона...")

initial_result = analyzer.analyze(template_path)

initial_requirements_count = sum(
    len(field.required_data)
    for field in initial_result.fields
)

print("\nПервичный результат:")
print("Тип документа:", initial_result.document_type)
print("Логических полей:", len(initial_result.fields))
print("Атомарных данных:", initial_requirements_count)


# -----------------------------
# Второй проход — проверка
# -----------------------------

print("\nПроверка результата...")

reviewed_result = analyzer.review(
    template_path,
    initial_result
)

reviewed_requirements_count = sum(
    len(field.required_data)
    for field in reviewed_result.fields
)

print("\nРезультат после проверки:")
print("Тип документа:", reviewed_result.document_type)
print("Логических полей:", len(reviewed_result.fields))
print("Атомарных данных:", reviewed_requirements_count)


# -----------------------------
# Полный результат
# -----------------------------

print("\nНайденные поля после проверки:")

for number, field in enumerate(reviewed_result.fields, start=1):

    print(f"\n{number}. {field.key}")
    print("Label:", field.label)
    print("Description:", field.description)

    print("Требуемые данные:")

    for requirement in field.required_data:
        print(
            f"  - {requirement.key}: "
            f"{requirement.description}"
        )