import unittest
import numpy as np
import imageio.v3 as iio
import sys
import os

# Get the absolute path of the current script
current_script_path = os.path.abspath(os.getcwd())

# Get the parent directory (one level up)
parent_directory = os.path.dirname(current_script_path)

# Add the parent directory to sys.path
sys.path.append(parent_directory)

# Import from the parent directory
from src.steganograph import *;

class TestMyModule(unittest.TestCase):
    def test_Embeding_txt_file(self):
        """
        Test embedding a text file into an image.
        """
        img_path = r'in/image_in.png'
        img_path_out = r'out/image_out_txt.png'
        file_path = r'in/Test_txt_file.txt'
        file_folder_out = 'out/'
        key = 'Test*123'

        # Embed data in the image
        img_path_out = Embed_data_in_img(
            img_path=img_path,
            img_path_out=img_path_out,
            file_path=file_path,
            key=key)

        # Extract data from the image and save to a file
        extract_data_img_save_file(
            img_path_out=img_path_out, 
            file_folder=file_folder_out, 
            key=key)

        # Compare the original and extracted text files
        with open(r'in/Test_txt_file.txt', 'rb') as f:
            file_txt_in = f.read()
        with open(r'out/Test_txt_file_out.txt', 'rb') as f:
            file_txt_out = f.read()
        result = file_txt_in == file_txt_out
        self.assertEqual(result, True)

    def test_Embeding_img_file(self):
        """
        Test subtraction of data from an image.
        """
        img_path = r'in/image_in.png'
        img_path_out = r'out/image_out_img.png'
        file_path = r'in/VeKings_NFT.png'
        file_folder_out = 'out/'
        key = 'Test*123'

        # Embed data in the image
        img_path_out = Embed_data_in_img(
            img_path=img_path,
            img_path_out=img_path_out,
            file_path=file_path,
            key=key)

        # Extract data from the image and save to a file
        extract_data_img_save_file(
            img_path_out=img_path_out, 
            file_folder=file_folder_out, 
            key=key)

        # Compare the original and extracted images
        file_img_in = iio.imread(r'in/VeKings_NFT.png')
        file_img_out = iio.imread(r'out/VeKings_NFT_out.png')
        result = np.array_equal(file_img_in, file_img_out)
        self.assertEqual(result, True)

if __name__ == "__main__":
    unittest.main()

