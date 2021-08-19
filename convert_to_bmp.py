from PIL import Image


def png_or_jpeg_to_bmp(source_file):
    file = Image.open(source_file)
    new_file = source_file+'.bmp'
    file.save(new_file)
    return new_file
