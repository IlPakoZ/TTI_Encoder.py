from chardet import detect
import argparse
import json
import math
import png
import secrets

MAXIMUM_SECRET_SEED_LENGTH = 2**32

# region Argument Parser

parser = argparse.ArgumentParser(description="Converts a plain text file into an image and generates a key.")
parser.add_argument("-f", "--filename", type=str, metavar="",
                    help="The name of the text file you want to convert (with its extension).")
parser.add_argument("-o", "--output", type=str, metavar="",
                    help="The name of the encoded output image file.")
args = parser.parse_args()

# endregion


def conversion(file_directory, output_file="converted.png"):

    # region Variables Declaration Namespace

    encoding = None
    text = None
    converted_text = ""
    color_list = []
    file_infos = {}
    session_id = secrets.randbelow(MAXIMUM_SECRET_SEED_LENGTH)

    # endregion

    # Detects the file's encoding
    try:
        with open(file_directory, "rb") as file:
            encoding = detect(file.read())
    except (FileNotFoundError, OSError):
        print("The specified file doesn't exist. The program will terminate.")
        exit(1)

    # Reads the file's text with the detected encoding
    try:
        with open(file_directory, "r", encoding=encoding["encoding"]) as file:
            text = "\n".join(file.read().splitlines())
    except (TypeError, UnicodeDecodeError):
        print("The specified image file is invalid. The program will terminate.")

    # Calculate the alphabet table
    try:
        file_infos = calculate_file_infos(text, encoding["encoding"], session_id)
        bits_length = file_infos["bits"]

        # Get the dictionary for encoding
        encoding_dic = generate_encoding_dic(file_infos)

        # Converts the text in bits
        for x in text:
            converted_text += get_bits(bits_length, encoding_dic[x], session_id)

        # Formats the binary text to create a valid color and to form a square
        converted_text = binary_formatting(file_infos, converted_text)
        # Splits values in lists of three tuples of 8 bits sequences
        color_list = binary_splitting(converted_text)

        # Saves the decoding key
        with open('key.json', 'w') as file:
            json.dump(file_infos, file, indent=4)

        image_creation(output_file, color_list)
    except TypeError:
        print("The file is empty!\n")


# Formats the binary text to create a valid color and to form a square
def binary_formatting(file_infos, binary_string):
    length = len(binary_string)
    file_infos["trailing"] = ((math.ceil(math.sqrt(math.ceil(length/24)))**2)*24 - length)
    binary_string += "0"*file_infos["trailing"]
    return binary_string


# Splits values in lists of three tuples of 8 bits sequences
def binary_splitting(binary_string):
    return create_square_array([get_integer(binary_string[x:x+8])
            for x in range(0, len(binary_string), 8)])


# Creates a square array
def create_square_array(color_array):
    dimension = int(math.sqrt(len(color_array)/3))
    square = [["" for x in range(dimension*3)] for y in range(dimension)]
    index = 0
    for y in range(dimension):
        for x in range(dimension*3):
            square[y][x] = color_array[index]
            index += 1
    return square


# Saves the image
def image_creation(output_file, rgb):
    with open(output_file, "wb") as f:
        w = png.Writer(len(rgb[0])//3, len(rgb))
        w.write(f, rgb)


# Gets the integer conversion of a binary number
def get_integer(sequence):
    return int(sequence, 2)


# Gets the binary conversion of an integer
def get_bits(bits, integer, session_id):
    return format(((integer+session_id) % 2**bits), "#0" + str(2+bits) + "b")[2:bits+2]


# Calculate the file infos that need to be saved
def calculate_file_infos(text, encoding, session_id):
    alphabet = calculate_alphabet(text)
    return {"encoding": encoding, "length": len(alphabet), "bits": math.ceil(math.log2(len(alphabet))),
            'keys': alphabet, 'session-id': hex(session_id)}


# Generates the dictionary that contains information to encode the characters
def generate_encoding_dic(file_infos):
    return {file_infos["keys"][j]: j for j in file_infos["keys"].keys()}


# Calculates which characters are into the file's text
def calculate_alphabet(text):
    s_text = set(text)
    try:
        s_text.remove(" ")
    except KeyError:
        pass
    temp = [x for x in s_text]
    temp.insert(0, " ")
    return {i: temp[i] for i in range(len(temp))}


# At startup, parses the arguments or asks for the user to input the file name
if __name__ == "__main__":
    if args.filename:
        filename = args.filename
    else:
        filename = input("Write the path of the file you want to convert: ")
    if args.output:
        conversion(filename, args.output)
    else:
        conversion(filename)
