import PyPDF2
from pdf2image import convert_from_path
from pdf_to_image import read_barcode


def pdf_text_extract(file_path):
    all_text = ""

    with open(file_path, 'rb') as file:
        pdf = PyPDF2.PdfReader(file)
        for page in pdf.pages:
            all_text += page.extract_text()
    return all_text


def create_dictionary_from_text(text):
    global company_name
    data_dict = {}

    # Разбиваем текст на строки
    lines = text.split('\n')
    company_name = lines[0]

    for line in lines:
        # Разбиваем каждую строку на ключ и значение
        parts = line.split(':', 1)

        # Если строка содержит две части (ключ и значение), добавляем в словарь
        if len(parts) == 2:
            key = parts[0].strip()
            value = parts[1].strip()
            data_dict[key] = value

    return data_dict


def process_values(data_dict):
    result_dict = dict()

    for key, value in data_dict.items():
        parts = value.split(':')
        extracted_keys = set()
        tmp_result_dict = dict()

        for i in range(len(parts) - 1):
            word = parts[i].split()[-1].strip()
            extracted_keys.add(word)
            tmp_result_dict[word] = parts[i + 1].strip()

        # Убираем добавленные ключ: значения из изначальной строки
        for extracted_key in extracted_keys:
            parts[0] = parts[0].replace(extracted_key, '').strip()

        # Обратно добавляем начальные ключ: значения
        result_dict[key] = parts[0].strip()
        # result_dict = {**result_dict, **tmp_result_dict}
        result_dict.update(tmp_result_dict)

    return result_dict


if __name__ == "__main__":
    pdf_path = 'task.pdf'

    images = convert_from_path(pdf_path)

    for i in range(len(images)):
        images[i].save('page' + str(i) + '.png', 'PNG')

    all_text = pdf_text_extract(pdf_path)
    # print(all_text)

    # Предположим что по условию ключи 'NOTES' и 'TAGGED BY' должны обязательно существовать
    preprocessed_text, notes = all_text.replace('TAGGED BY:', 'TAGGED BY: tmp_bar_code').rsplit('NOTES:', 1)
    if preprocessed_text is None or len(preprocessed_text) == 0:
        print('No text found')
    elif notes is None or len(notes) == 0:
        print('No notes found')

    dictionary = create_dictionary_from_text(preprocessed_text)
    dictionary['NOTES'] = notes
    processed_dict = process_values(dictionary)
    bar_code = read_barcode('page0.png')
    processed_dict['TAGGED BY'] = bar_code[0]
    extra_details = {'company_name': company_name, 'big_bar_code': bar_code[1]}
    processed_dict = {**extra_details, **processed_dict}
    print(processed_dict)

    expected_keys = ['PN', 'SN', 'DESCRIPTION', 'LOCATION', 'CONDITION', 'RECEIVER#', 'UOM', 'EXP DATE', 'PO',
                     'CERT SOURCE', 'REC.DATE', 'MFG', 'BATCH#', 'DOM', 'REMARK', 'LOT#', 'TAGGED BY', 'Qty', 'NOTES']

    missing_keys = [key for key in expected_keys if key not in processed_dict]
    assert not missing_keys, f"Не все ключи представлены в словаре: {', '.join(missing_keys)}"
