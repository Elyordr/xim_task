from PIL import Image
from pyzbar.pyzbar import decode


def read_barcode(image_path):
    final_codes = []
    img = Image.open(image_path)

    # Декодирование шрих-кода
    decoded_objects = decode(img)

    for obj in decoded_objects:
        final_codes.append(obj.data.decode('utf-8'))
    return final_codes
