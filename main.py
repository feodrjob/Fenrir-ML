import fitz # Официальное имя библиотеки pymypdf

#Название файля откуда читаем
pdf_path = "Защита ГЩУ-ТЭЦ-3 от БПЛА  ОСНОВА.pdf"

#Открываем документ (закроется сам при выходе из with)
with fitz.open(pdf_path) as doc:
    #итаем 1ю и 3ю страницы (там нужная информация)
    page_1 = doc[0]
    text_page_1 = page_1.get_text() # Вытаскиваем весь текст со страницы

    page_3 = doc[2]
    text_page_3 = page_3.get_text()

#Сохраняем результат в текстовый файл

with open ("extracted_text.txt", "w", encoding="utf-8") as file:
    file.write("--- СТРАНИЦА 1 ---\n")
    file.write(text_page_1)
    file.write("\n\n--- СТРАНИЦА 3 ---\n")
    file.write(text_page_3)

print("Текст успешно извлечен и сохранен в extracted_text.txt")
