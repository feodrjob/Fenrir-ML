from src.templates.template_slot_detector import detect_template_slots


template_path = "templates/aosr_344_source.docx"

slots = detect_template_slots(template_path)

print("Найдено физических мест заполнения:", len(slots))

for number, slot in enumerate(slots, start=1):

    print(f"\n--- SLOT {number} ---")

    print(
        "Положение:",
        f"table={slot.table_index},",
        f"row={slot.row_index},",
        f"cell={slot.cell_index}"
    )

    print("Ширина:", slot.grid_span)
    print("Строка:", slot.row_text)
    print("Выше:", slot.previous_text)
    print("Ниже:", slot.next_text)




    """
    pdf -> текст -> llm -> значение
    """