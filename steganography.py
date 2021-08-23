# Steganography app by meshkov sergey
# bmp(png,jpg) to modified bmp
# use function write_message_to_bmp(path_file, message) to put message in bmp file
# example, write_message_to_bmp('example.bmp', 'wonderful message for you'):
# use function read_message_from_bmp(path_file) to get message from bmp file
# example, read_message_from_bmp('example.bmp') -> output:'wonderful message for you'
from bitstring import BitArray
from PIL import Image


def convert_to_bmp(source_file):
    """Convert png or jpeg to bmp"""
    file = Image.open(source_file)
    new_file = source_file[:-4] + '_with_message.bmp'
    file.save(new_file)
    return new_file


def rec_information(data_ints, message_size_in_bytes):
    """Запись в список int информации о размере текстового сообщения в байтах"""
    interval_bytes = int.to_bytes(message_size_in_bytes, length=4, byteorder='big')
    interval_ints = [byte for byte in interval_bytes]
    data_ints = data_ints[:6] + interval_ints + data_ints[10:]
    return data_ints


def from_char_to_bits(char):
    encoded_bytes = str.encode(char, 'utf-8')
    bits = BitArray(encoded_bytes)
    bits_array_ints = [int(bit) for bit in bits]
    return bits_array_ints


def from_bits_to_char(bits):
    number = 0
    for index, bit in enumerate(bits):
        number += 2**(7-index)*bit
    bytes_encoded = int.to_bytes(number, length=1, byteorder='big')
    char = bytes.decode(bytes_encoded, 'utf-8')
    return char


def from_bits_to_int(bits):
    number = 0
    for index, bit in enumerate(bits):
        number += 2**(7-index)*bit
    return number


def get_parametres_of_bmp_file(path_file):
    with open(path_file, 'rb') as file:
        file.seek(2)
        bytes_size_of_file = file.read(2)
        size_of_file = int.from_bytes(bytes_size_of_file, byteorder='little')
        file.seek(10)
        bytes_offset_of_image = file.read(4)
        offset_of_image = int.from_bytes(bytes_offset_of_image, byteorder='little')
        size_of_image = size_of_file - offset_of_image
        file.seek(6)
        size_of_message = int.from_bytes(file.read(4), byteorder='big')
        result = {'size_of_file': size_of_file, 'offset_of_image': offset_of_image,
                  'size_of_image': size_of_image, 'size_of_message': size_of_message}
        return result


def calculate_interval(size_of_image, message=0, size_of_message=0):
    """Расчет интервала между байтами, содержащими изображение"""
    if message:
        message_bytes = message.encode('utf-8')
        interval = int(int(size_of_image/len(message_bytes))/8)
        if interval >= 1:
            return interval
        else:
            return -1
    elif size_of_message:
        interval = int(int(size_of_image/size_of_message)/8)
        return interval
    else:
        return -1


def write_message_to_bmp(path_file, message):
    """Запись сообщения в bmp-файл"""
    path_file = convert_to_bmp(path_file)
    bmp_parametres = get_parametres_of_bmp_file(path_file)
    interval = calculate_interval(message=message, size_of_image=bmp_parametres.get('size_of_image'))
    if interval == -1:
        return False
    with open(path_file, 'r+b') as file:
        data_bytes = bytes(file.read())
        data_ints = [one_byte for one_byte in data_bytes]
        data_ints = rec_information(data_ints,  len(message.encode('utf-8')))
        index = bmp_parametres.get('offset_of_image')
        for char in message:
            char_bits = from_char_to_bits(char)
            for i in range(len(char_bits)):
                byte = int.to_bytes(data_ints[index], length=1, byteorder='big')
                bits = BitArray(byte)
                bits_array_int = [int(bit) for bit in bits]
                bits_array_int[7] = char_bits[i]
                data_ints[index] = from_bits_to_int(bits_array_int)
                index += interval
        data_bytes_modified = bytes(data_ints)
        file.seek(0)
        file.write(data_bytes_modified)
    return True


def read_message_from_bmp(path_file):
    """Чтение сообщения из bmp-файла"""
    bmp_parametres = get_parametres_of_bmp_file(path_file)
    interval = calculate_interval(size_of_message=bmp_parametres.get('size_of_message'),
                                  size_of_image=bmp_parametres.get('size_of_image'))
    with open(path_file, 'rb') as file:
        data_bytes = bytes(file.read())
        data_ints = [one_byte for one_byte in data_bytes]
        index = bmp_parametres.get('offset_of_image')
        message_bits = []
        message_ints = []
        for i in range(bmp_parametres.get('size_of_message') * 8):
            byte = int.to_bytes(data_ints[index], length=1, byteorder='big')
            bits = BitArray(byte)
            bits_array_int = [int(bit) for bit in bits]
            message_bits.append(bits_array_int[7])
            index += interval
        for ind, val in enumerate(message_bits):
            if (ind+1) % 8 == 0:
                message_ints.append(from_bits_to_int(message_bits[ind-7:ind+1]))
        message_bytes = bytes(message_ints)
        message = bytes.decode(message_bytes, 'utf-8')
        return message


if __name__ == '__main__':
    path = 'file_100x100x24.bmp'
    path2 = 'file_100x100x24_with_message.bmp'
    if write_message_to_bmp(path, 'привет, neo'):
        print(read_message_from_bmp(path2))
