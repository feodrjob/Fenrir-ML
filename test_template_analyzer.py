from src.templates.template_analyzer import extract_template_text


template_path = "templates/aosr_344_source.docx"

template_text = extract_template_text(template_path)

print("Текст шаблона:")
print("--------------------")
print(template_text)

print("\n--------------------")
print("ПРОВЕРКА ШАБЛОНА")
print("--------------------")

required_phrases = [
    "освидетельствования скрытых работ",
    "1. К освидетельствованию предъявлены следующие работы",
    "3. При выполнении работ применены",
    "7. Разрешается производство последующих работ",
]

missing_phrases = []

for phrase in required_phrases:
    if phrase not in template_text:
        missing_phrases.append(phrase)


if missing_phrases:
    print("Не найдены некоторые части шаблона:")

    for phrase in missing_phrases:
        print("-", phrase)

else:
    print("Все контрольные части шаблона найдены.")


print("Количество символов:", len(template_text))