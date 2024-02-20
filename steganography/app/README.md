# Introduction

I created this package to embed a data file into a image file by steganography technique.
<br>
The package use sha512(key) to encrypt data before embedded it in the image. 
<br> 
This package same the data file in the LSB of the color bytes, so the average modification of the pixel is around 1/128=0.78%, so is hard to detect this modification by necked eye. 
<br> 
The size of the image before and after data embedding is almost the same. and this package embed the data, the file name and its extension to be extracted correctly

**The package use the below libraries:**
 <br>hashlib, imageio, numpy, os, re

# Installation

You can install the package by the pip command below

pip install steganograph==0.0.12

# How to use the package

### Import libraries


```python
import imageio.v3 as iio
import numpy as np
```


```python
from steganograph import *
```

### Test embedding and extract a text file into an image.

Path of the files and the key of cryptography


```python
img_path = r'in/image_in.png'
img_path_out = r'out/image_out_txt.png'
file_path = r'in/Test_txt_file.txt'
file_folder_out = 'out/'
key = 'Test*123'
```

Embed data in the image


```python
img_path_out = Embed_data_in_img(
    img_path=img_path,
    img_path_out=img_path_out,
    file_path=file_path,
    key=key)
```

    out/image_out_txt.png is saved successfully
    

Extract data from the image and save to a file


```python
extract_data_img_save_file(
    img_path_out=img_path_out, 
    file_folder=file_folder_out, 
    key=key)
```

    out/Test_txt_file_out.txt is written successfully
    




    'out/Test_txt_file_out.txt'



**Compare the original and extracted text files**


```python
with open(r'in/Test_txt_file.txt', 'r') as f:
    file_txt_in = f.read()
    f.close()
with open(r'out/Test_txt_file_out.txt', 'r') as f:
    file_txt_out = f.read()
    f.close()
file_txt_in == file_txt_out
```




    True



The original and the extracted text files are the same 

Compare the text content by print of the original and the extracted text


```python
print(file_txt_in)
```

    Below an example of text file that we can head in the image file
    
    Bitcoin Address
    13daa8SYB8L5b8hcrkBfABskDzju53A3PR
    Private Key
    L58FrKEB6p9EMdBWsG5njdLVRnafUJHff3Xz3uy2VMo2GLJU4PAG
    
    My PW: JQSqju*/66587sa
    


```python
print(file_txt_out)
```

    Below an example of text file that we can head in the image file
    
    Bitcoin Address
    13daa8SYB8L5b8hcrkBfABskDzju53A3PR
    Private Key
    L58FrKEB6p9EMdBWsG5njdLVRnafUJHff3Xz3uy2VMo2GLJU4PAG
    
    My PW: JQSqju*/66587sa
    

___
The original text and the extracted are the same

The original image vs the modified one

<div   style='float: left;width: 33.33%;padding: 5px;'>
  <p style="text-align:center;"> Original image </p> 
  <img src='https://bouz1.github.io/fils/steganography/images/image_in.png'>
</div>

<div   style='float: left;width: 33.33%;padding: 5px;'>
  <p style="text-align:center;"> Image Image with data embedded</p> 
  <img src='https://bouz1.github.io/fils/steganography/images/image_out_txt.png'>
</div>

### Test embedding and extract a img file into an image.

Path of the files and the key of cryptography


```python
img_path = r'in/image_in.png'
img_path_out = r'out/image_out_img.png'
file_path = r'in/VeKings_NFT.png'
file_folder_out = 'out/'
key = 'Test*123'
```

Embed data in the image


```python
img_path_out = Embed_data_in_img(
    img_path=img_path,
    img_path_out=img_path_out,
    file_path=file_path,
    key=key)
```

    out/image_out_img.png is saved successfully
    

Extract data from the image and save to a file


```python
extract_data_img_save_file(
    img_path_out=img_path_out, 
    file_folder=file_folder_out, 
    key=key)
```

    out/VeKings_NFT_out.png is written successfully
    




    'out/VeKings_NFT_out.png'



**Compare the original and extracted images**


```python
file_img_in = iio.imread(r'in/VeKings_NFT.png')
file_img_out = iio.imread(r'out/VeKings_NFT_out.png')
result = np.array_equal(file_img_in, file_img_out)
```

<div   style='float: left;width: 33.33%;padding: 5px;'>
  <p style="text-align:center;"> Original image </p> 
  <img src='https://bouz1.github.io/fils/steganography/images/VeKings_NFT.png'>
</div>

<div   style='float: left;width: 33.33%;padding: 5px;'>
  <p style="text-align:center;"> Image Image with data embedded</p> 
  <img src='https://bouz1.github.io/fils/steganography/images/VeKings_NFT_out.png'>
</div>

The original image vs the modified one

<div   style='float: left;width: 33.33%;padding: 5px;'>
  <p style="text-align:center;"> Original image </p> 
  <img src='https://bouz1.github.io/fils/steganography/images/image_in.png'>
</div>

<div   style='float: left;width: 33.33%;padding: 5px;'>
  <p style="text-align:center;"> Image Image with data embedded</p> 
  <img src='https://bouz1.github.io/fils/steganography/images/image_out_img.png'>
</div>
