# Загружаем настройки из файла .env
from dotenv import load_dotenv

# Сам клиент GigaChat
from gigachat import GigaChat

# Классы SDK для создания структурированного запроса
from gigachat.models import (
    ChatCompletionRequest,
    ChatMessage,
    ChatModelOptions,
    ChatResponseFormat
)


# Читаем GIGACHAT_CREDENTIALS и GIGACHAT_SCOPE из .env
load_dotenv()


# ---------------------------------------------------------
# 1. Читаем РЕАЛЬНЫЙ текст, который ранее извлёк PyMuPDF
# ---------------------------------------------------------

with open("data/input/extracted_text.txt", "r", encoding="utf-8") as file:
    document_text = file.read()


# ---------------------------------------------------------
# 2. Описываем строгую структуру ответа модели
#
# Это практически та же JSON Schema,
# которую мы уже использовали с Ollama.
# ---------------------------------------------------------

extraction_schema = {
    "type": "object",

    "properties": {
        "project_code": {
            "anyOf": [
                {"type": "string"},
                {"type": "null"}
            ]
        },

        "material": {
            "anyOf": [
                {"type": "string"},
                {"type": "null"}
            ]
        },

        "quantity": {
            "anyOf": [
                {"type": "string"},
                {"type": "null"}
            ]
        },

        "thickness": {
            "anyOf": [
                {"type": "string"},
                {"type": "null"}
            ]
        }
    },

    # Все четыре ключа должны присутствовать в JSON
    "required": [
        "project_code",
        "material",
        "quantity",
        "thickness"
    ],

    # Модель не может добавить какие-то свои поля
    "additionalProperties": False
}


# ---------------------------------------------------------
# 3. Формируем инструкцию модели
# ---------------------------------------------------------

prompt = f"""
Ты анализируешь рабочую документацию.

Найди:
- шифр всей рабочей документации;
- материал "Бронеплёнка противоосколочная";
- количество именно этой бронеплёнки;
- толщину именно этой бронеплёнки.

Не путай шифр рабочей документации
с обозначениями отдельных деталей.

ВАЖНО:
копируй значения максимально близко к исходному тексту.
Не пересчитывай и не переводи единицы измерения.
Если значения нет в документе — верни null.
Ничего не придумывай.

Текст документа:

{document_text}
"""


# ---------------------------------------------------------
# 4. Создаём запрос для GigaChat
# ---------------------------------------------------------

request = ChatCompletionRequest(

    # Явно выбираем бесплатную модель,
    # которую мы решили использовать для разработки
    model="GigaChat-2",

    # Передаём текст модели как сообщение пользователя
    messages=[
        ChatMessage(
            role="user",
            content=prompt
        )
    ],

    # Здесь находится настройка Structured Output
    model_options=ChatModelOptions(

        response_format=ChatResponseFormat(

            # Ответ должен быть JSON
            type="json_schema",

            # И соответствовать нашей схеме
            schema=extraction_schema,

            # Требуем строго соблюдать схему
            strict=True
        )
    )
)


# ---------------------------------------------------------
# 5. Создаём соединение с GigaChat
# ---------------------------------------------------------

with GigaChat(

    # Сертификат, который мы только что скачали
    ca_bundle_file="russian_trusted_root_ca_pem.crt"

) as client:

    print("Отправляю текст документа в GigaChat...")

    # Отправляем сформированный выше запрос
    response = client.chat.create(request)

    print("GigaChat ответил:")

    # В ответе GigaChat текст лежит внутри messages -> content
    answer = response.messages[0].content[0].text

    print(answer)