from setuptools import find_packages, setup

with open("app/README.md", "r") as f:
    long_description = f.read()

setup(
    name="steganograph",
    version="0.0.14",
    description="Head a file in img and extracted without chnaging the image size and you can protect your file with a password",
    package_dir={"": "app"},
    packages=find_packages(where="app"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bouz1/PypiContributions/tree/main/steganography",
    author="Abb BOZZ",
    author_email="bozzabb1@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    

    #install_requires=[],
    extras_require={
        "dev": ['hashlib','imageio','numpy','os','re'],
    },
    python_requires=">=3.7",
)
