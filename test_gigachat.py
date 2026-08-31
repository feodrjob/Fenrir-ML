from dotenv import load_dotenv
from gigachat import GigaChat

load_dotenv()


with GigaChat(
    model="GigaChat-2",
    ca_bundle_file="russian_trusted_root_ca_pem.crt"
) as client:

    print("Получаю список доступных моделей...")

    # Спрашиваем у GigaChat API,
    # какие модели доступны именно нашему аккаунту
    models = client.get_models()

    # Выводим название каждой доступной модели
    for model in models.data:
        print(model.id_)