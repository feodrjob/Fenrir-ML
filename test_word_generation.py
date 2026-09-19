from src.rendering.word_renderer import WordRenderer


renderer = WordRenderer()

context = {
    "project_code": "3Э-1246.00"
}

renderer.render(
    template_path="templates/aosr_344_template.docx",
    output_path="data/output/generated_aosr.docx",
    context=context
)

print("DOCX успешно сгенерирован")