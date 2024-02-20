import imageio.v3 as iio
import numpy as np
import datetime
import os
import re
import hashlib

nb_bytes_size=4



def bytes_arr_to_bin_str(arr):
    """
    Converts an array of bytes to a binary string representation.
    Args:
        arr (list): A list of bytes (integers in the range 0-255).
    Returns:
        str: A binary string where each byte is represented by 8 bits.
    """
    # Join the binary representation of each byte in the array
    # using 'format(c, '08b')', which ensures each byte is represented
    # as an 8-character binary string (padded with leading zeros if needed)
    return ''.join([format(c, '08b') for c in arr])





def file_to_arr(file_path):
    """
    Reads a binary file and converts its content to an array of bytes.
    Args:
        file_path (str): Path to the binary file.
    Returns:
        list: An array of bytes representing the file content.
            The format is: [title_size_bytes, size_bytes, title_bytes, data_bytes]
    """
    try:
        # Open the file in binary read mode
        with open(file_path, mode='rb') as file:
            # Read the entire content of the file
            fileContent = file.read()
        # Close the file
        file.close()
    except Exception as e:
        # Print any exception encountered during file reading
        print(e)
        return None
    # Convert the file content to an array of bytes
    data_bytes = [c for c in fileContent]
    # Calculate the size of the data_bytes array
    size = len(data_bytes)
    # Convert the size (integer) to a bytes array of nb_bytes_size bytes
    size_bytes = [x for x in size.to_bytes(nb_bytes_size, 'big')]
    # Extract the title from the file path
    title = os.path.basename(file_path)
    # Take only the last 255 bytes of the title (if it's longer)
    title = title[-255:]
    # Convert the title string to an array of ASCII values (bytes)
    title_bytes = [ord(c) for c in title]
    title_size_bytes=[len(title_bytes)]
    # Create an array containing the title size, size bytes, title bytes, and data bytes
    file_arr_bytes = title_size_bytes + size_bytes + title_bytes + data_bytes
    return file_arr_bytes




def split_file_arr(arr):
    
    title_size=arr[0]
    
    start=1
    stop=nb_bytes_size+1
    size_bytes=arr[start:stop]
    size=int.from_bytes(size_bytes, "big")
    
    start=stop
    stop=start+title_size
    
    title_bytes=arr[start:stop]
    title=''.join([chr(x) for x in  title_bytes])
    
    start=stop
    stop=start+size
    data_bytes=arr[start:stop]
    return title_size, size, title,data_bytes








def split_file_arr(arr):
    """
    Splits an array of bytes representing file content into meaningful components.
    Args:
        arr (list): An array of bytes representing the file content.
            The format is: [title_size_bytes, size_bytes, title_bytes, data_bytes]

    Returns:
        tuple: A tuple containing the following components:
            - title_size (int): The length of the title (in bytes).
            - size (int): The size of the data (number of bytes).
            - title (str): The title extracted from the file content.
            - data_bytes (list): The actual content of the file (as an array of bytes).
    """
    # Extract the title size from the first element of the array
    title_size = arr[0]
    # Extract the size of the data from the next nb_bytes_size elements
    start = 1
    stop = nb_bytes_size + 1
    size_bytes = arr[start:stop]
    size = int.from_bytes(size_bytes, "big")
    # Extract the title from the subsequent title_size elements
    start = stop
    stop = start + title_size
    title_bytes = arr[start:stop]
    title = ''.join([chr(x) for x in title_bytes])
    # Extract the data content from the remaining size elements
    start = stop
    stop = start + size
    data_bytes = arr[start:stop]
    # Return the extracted components as a tuple
    return title_size, size, title, data_bytes





def pw_hash(pw="test", n=1):
    """
    Hashes a password using SHA-512 algorithm and returns an array of integers.
    Args:
        pw (str, optional): The password to be hashed (default is "test").
        n (int, optional): Number of iterations (default is 1).
    Returns:
        np.ndarray: An array of integers representing the hashed password.
    """
    # Initialize 'has' with the SHA-512 hash of the input password
    has = hashlib.sha512(pw.encode('utf-8')).hexdigest()
    arr = []  # Initialize an empty list to store intermediate results
    i = 0
    # Repeat until the length of 'arr' reaches 'n'
    while len(arr) < n:
        i += 1
        # Compute the SHA-512 hash of '(has + str(i))'
        has = hashlib.sha512((has + str(i)).encode('utf-8')).hexdigest()
        # Split the resulting hash into pairs of characters
        arr2 = re.findall('..', has)
        # Extend 'arr' with these pairs
        arr += arr2
    # Convert each pair of characters from hexadecimal to decimal
    return np.array([int(x, 16) for x in arr])



def encrept(arr, key):
    """
    Encrypts a list of values using a secret key.
    Args:
        arr (list): The input list (message or data).
        key (str): A secret key for encryption.
    Returns:
        list: The encrypted output list.
    """
    # Calculate the length of the input list
    length_msg = len(arr)
    # Generate a key array by hashing the input key
    key_arr = pw_hash(pw=key, n=length_msg)
    # Initialize an empty list to store the encrypted output
    out = []
    # Perform the encryption operation for each element in the input list
    for i, x in enumerate(arr):
        # Add the corresponding element from the key array to the current element
        encrypted_value = (x + key_arr[i]) % 256
        # Append the encrypted value to the output list
        out.append(encrypted_value)
    # Return the resulting encrypted list
    return out




def decrept(arr, key):
    """
    Decrypts a message using a given key.

    Args:
        arr (list[int]): A list of integers representing the encrypted message.
        key (str): The decryption key.

    Returns:
        list[int]: A list of integers representing the decrypted message.
    """
    # Calculate the length of the message
    lenght_msg = len(arr)
    
    # Generate an array of hash values based on the key
    key_arr = pw_hash(pw=key, n=lenght_msg)
    
    # Decrypt each element in the input array
    out = [(256 + x - key_arr[i]) % 256 for i, x in enumerate(arr)]
    
    return out
    
    
    
def img_flatten(img_path):
    """
    Reads an image from the specified path and flattens it.
    Args:
        img_path (str): Path to the image file.
    Returns:
        tuple: A tuple containing:
            - img_flat (numpy.ndarray): Flattened array of pixel values.
            - img_shape (tuple): Shape of the original image (height, width, channels).
    """
    try:
        # Read the image from the given path
        img = iio.imread(img_path)
    except Exception as e:
        # Print any exception encountered during image reading
        print(e)
        return None
    # Flatten the image into a 1D array of pixel values
    img_flat = img.flatten()
    # Get the shape of the original image (height, width, channels)
    img_shape = img.shape
    # Return the flattened array and image shape
    return img_flat, img_shape

    
    
    
def extract_sizes(img_path, key='123'):
    """
    Extracts the least significant bit (LSB) of each pixel value in the image 
    that represent the size part.
    Args:
        img_path (str): Path to the input image file.
        key (str, optional): Secret key for encryption (default is '123').
    Returns:
        list: A list of LSB values (0 or 1) extracted from the image header.
    """
    # Flatten the input image and get its shape
    img_flat, img_shape = img_flatten(img_path)
    # Extract the least significant bit (LSB) of each pixel value
    # from the first 8*(nb_bytes_size+1) elements of the flattened image
    return [x % 2 for x in img_flat[:8 * (nb_bytes_size + 1)]]





def extract_last_bytes_from_img(img_flat_part):
    """
    Extracts the least significant bit (LSB) of each pixel value in the given flattened image part.
    Args:
        img_flat_part (list): A portion of the flattened image (list of pixel values).
    Returns:
        list: A list of integers representing the extracted last bytes from each pixel.
    """
    # Calculate the last bit (LSB) for each pixel value
    last_bits = [str(x % 2) for x in img_flat_part]
    # Join the LSBs to form a binary string
    last_bits = ''.join(last_bits)
    # Split the binary string into chunks of 8 bits (1 byte)
    last_bits = re.findall('........', last_bits)
    # Convert each byte from binary to integer
    last_bytes = [int(x, 2) for x in last_bits]
    return last_bytes









# This function extracts data from an image using steganography techniques.
# It assumes that the image contains hidden data in its header.

def extract_data_img(img_path, key='123'):
    """
    Extracts data from an image using steganography techniques.
    Args:
        img_path (str): Path to the input image file.
        key (str, optional): Secret key for decryption (default is '123').
    Returns:
        tuple: A tuple containing:
            - title_size (int): The length of the title (in bytes).
            - size (int): The size of the data (number of bytes).
            - title (str): The title extracted from the image header.
            - data_part (list): The actual data content extracted from the image.
    """
    # Flatten the input image and get its shape
    img_flat, img_shape = img_flatten(img_path)
    
    # Extract the data size and title size from the image
    size_part = img_flat[:8 * (nb_bytes_size + 1)]
    size_part = extract_last_bytes_from_img(size_part)
    size_part = decrept(size_part, key)
    title_size = size_part[0]
    size = size_part[1:]
    size = int.from_bytes(size, "big")
    
    # Extract the title data
    start = 8 * (nb_bytes_size + 1)
    stop = start + (title_size + size) * 8
    title_data = img_flat[0:stop]
    title_data = extract_last_bytes_from_img(title_data)
    title_data = decrept(title_data, key)
    
    # Extract the title and data content
    start = nb_bytes_size + 1
    stop = start + title_size
    title_part = title_data[start:stop]
    title = ''.join([chr(x) for x in title_part])
    start = stop
    stop = start + size
    data_part = title_data[start:stop]
    
    return title_size, size, title, data_part