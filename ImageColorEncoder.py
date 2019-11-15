from chardet import detect
import json
import math
import png


def conversion(file_directory):
    encoding = None
    text = None
    converted_text = ""
    color_list = []
    file_infos = {}
    output_file = "converted.png"

    # Detects the file's encoding
    try:
        with open(file_directory, "rb") as file:
            encoding = detect(file.read())
    except (FileNotFoundError, OSError):
        print("The specified file doesn't exist. The program will terminate.")
        exit(1)

    # Reads the file's text with the detected encoding
    with open(file_directory, "r", encoding=encoding["encoding"]) as file:
        text = "\n".join(file.read().splitlines())

    # Calculate the alphabet table
    try:
        file_infos = calculate_file_infos(text, encoding["encoding"])
        bits_length = file_infos["bits"]

        # Get the dictionary for encoding
        encoding_dic = generate_encoding_dic(file_infos)

        # Converts the text in bits
        for x in text:
            converted_text += get_bits(bits_length, encoding_dic[x])

        # Formats the binary text to create a valid color and to form a square
        converted_text = binary_formatting(converted_text)
        # Splits values in lists of three tuples of 8 bits sequences
        color_list = binary_splitting(converted_text)

        # Saves the decoding key
        with open('key.json', 'w') as file:
            json.dump(file_infos, file, indent=4)

        image_creation(output_file, color_list)
    except TypeError:
        print("The file is empty!\n")


# Formats the binary text to create a valid color and to form a square
def binary_formatting(binary_string):
    length = len(binary_string)
    binary_string += "0"*((math.ceil(math.sqrt(math.ceil(length/24)))**2)*24 - length)
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
    with open(output_file,"wb") as f:
        w = png.Writer(len(rgb[0])//3, len(rgb))
        w.write(f, rgb)


# Checks if the conversion worked
def checksum(bits, string, decoding_dic):
    converted_text = ""

    try:
        for x in range(0, len(string), bits):
            converted_text += decoding_dic[get_integer(string[x:x+bits])]
    except IndexError:
        print("Binary sequence is invalid!")
    return converted_text


# Gets the integer conversion of a binary number
def get_integer(sequence):
    return int(sequence, 2)


# Gets the binary conversion of an integer
def get_bits(bits, integer):
    return format(integer, "#0" + str(2+bits) + "b")[2:bits+2]


# Calculate the file infos that need to be saved
def calculate_file_infos(text, encoding):
    alphabet = calculate_alphabet(text)
    return {"encoding": encoding, "length": len(alphabet), "bits": math.ceil(math.log2(len(alphabet))), 'keys': alphabet}


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


conversion(input("Write the path of the file you want to convert: "))
