import png
import json


def conversion(image, key):
    img = []
    file_infos = {}

    # Loads the key into memory
    try:
        file_infos = load_key(key)
    except (FileNotFoundError, OSError):
        print("The key file doesn't exist. The program will terminate.")
        exit(1)

    # Loads the image into memory
    try:
        img = load_image(image)
    except (FileNotFoundError, OSError):
        print("Image file not found. The program will terminate.")
        exit(1)

    # Gets binary code from image and removes the trailing zeros used to create a squared image
    binary_text = remove_trailing_zeros(file_infos["bits"], get_binary(img))

    # Decodes the binary into characters
    decoded_text = decode(file_infos["bits"], binary_text, file_infos["keys"])

    while True:
        try:
            result = input("Type the path of the decoded text: ")
            with open(result, "w", encoding=file_infos["encoding"]) as f:
                f.write(decoded_text)
        except (FileNotFoundError, OSError):
            print("Invalid path. Please retry.\n")
        finally:
            break


# Get binary code from RGB Values
def get_binary(img):
    return "".join([get_bits(8, x) for x in img])


# Loads the file containing the key
def load_key(key):
    file_infos = {}
    with open(key, "r") as f:
        file_infos = json.load(f)
    return file_infos


# Converts the binary sequence in text
def decode(bits, string, decoding_dic):
    converted_text = ""

    try:
        for x in range(0, len(string), bits):
            converted_text += decoding_dic[str(get_integer(string[x:x+bits]))]
    except (IndexError, KeyError, TypeError):
        print("\nBinary sequence, key or image file invalid or damaged! The program will terminate!")
        exit(1)
    return converted_text


# Gets the integer conversion of a binary number
def get_integer(sequence):
    return int(sequence, 2)


# Gets the binary conversion of an integer
def get_bits(bits, integer):
    return format(integer, "#0" + str(2+bits) + "b")[2:bits+2]


# Loads the image and converts it into an array of numbers.
def load_image(image):
    img = []
    with open(image, mode='rb') as f:
        reader = png.Reader(file=f)
        w, h, png_img, _ = reader.asRGB8()
        for line in png_img:
            for i in range(len(line)):
                img.append(line[i])
    return img


# Removes the useless trailing zeros
def remove_trailing_zeros(bits, binary_text):
    length = len(binary_text)
    index = length
    last_index = -1
    while True:
        if get_integer(binary_text[index-bits:index]) == 0:
            last_index = index - bits
            index -= bits
        else:
            break
    untrailed_text = None
    if last_index != -1:
        untrailed_text = binary_text[0:last_index]
    return untrailed_text


img_path = input("Type the path of the image you want to decode: ")
key_path = input("Type the path of the deciphering key: ")

conversion(img_path, key_path)
