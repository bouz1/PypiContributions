from .utils import *


        
        
        
        

def Embed_data_in_img(img_path, img_path_out,file_path, key='123'):
    """
    Embeds data from a file into the header of an image.
    Args:
        img_path (str): Path to the input image file.
        file_path (str): Path to the binary file containing data to embed.
        key (str, optional): Secret key for encryption (default is '123').
    Returns:
        str or None: Path to the output image file with embedded data (or None if unsuccessful).
    """
    # Flatten the input image and get its shape
    img_flat, img_shape = img_flatten(img_path)
    # Read the data from the specified file and encrypt it
    arr_file = file_to_arr(file_path)
    arr_enc = encrept(arr_file, key)
    # Convert the encrypted data to a binary string
    arr_str_bits = bytes_arr_to_bin_str(arr_enc)
    # Check if the image can accommodate the data
    if len(img_flat) < len(arr_str_bits):
        print('The size of the file is larger than the image capacity')
        return None
    else:
        # Embed each bit of the data into the image pixels
        for i in range(len(arr_str_bits)):
            img_flat[i] = ((img_flat[i] >> 1) << 1) + int(arr_str_bits[i])
        # Convert the modified flattened array back to uint8
        img_flat = img_flat.astype(np.uint8)
        # Reshape the modified array to match the original image shape
        img_out = img_flat.reshape(img_shape)
        # Save the modified image
        iio.imwrite(img_path_out, img_out)
        print(img_path_out, 'is saved successfully')
        return img_path_out
    
    

    
    
    

def extract_data_img_save_file(img_path_out, file_folder, key='123'):
    """
    Extracts data from an image and saves it to a file.
    Args:
        img_path (str): Path to the input image file.
        file_folder (str): Path to the folder where the output file will be saved.
        key (str, optional): Secret key for decryption (default is '123').
    Returns:
        str or None: Path to the saved output file (or None if unsuccessful).
    """
    # Extract data from the image
    title_size, size, title, data_part = extract_data_img(img_path=img_path_out, key=key)
    # Split the file title and extension
    title = os.path.splitext(title) 
    # Append '_out' to the base title and reattach the extension
    title = title[0] + '_out' + title[1]
    # Create the file path
    file_path = os.path.join(file_folder, title)
    try:
        # Write the data to the file
        with open(file_path, "wb") as file:
            file.write(bytes(data_part))
            print(file_path, 'is written successfully')
            return file_path
        file.close()
    except Exception as e:
        print(e)
        return None
        
    