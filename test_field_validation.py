from src.validation.field_validation import validate_field


tests = [
    ("thickness", "200 мкм"),
    ("thickness", "200 кг"),

    ("quantity", "162 м²"),
    ("quantity", "15 шт"),
    ("quantity", "много"),

    ("project_code", "3Э-1246.00"),
    ("project_code", "ПРОЕКТ"),

    ("material", "Бронеплёнка противоосколочная"),
]


for field_name, value in tests:
    result = validate_field(
        field_name,
        value
    )

    print(
        field_name,
        value,
        "->",
        result.status,
        "|",
        result.reason
    )