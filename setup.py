import setuptools


with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="stream_data_processor",
    version="0.0.1",

    description="Processing streaming data",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="Mystique",

    package_dir={"": "stream_data_pipe"},
    packages=setuptools.find_packages(where="stream_data_processor"),

    install_requires=[
        "aws-cdk.core>=1.31.0",
    ],

    python_requires=">=3.6",

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",

        "License :: OSI Approved :: Apache Software License",

        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",

        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",

        "Typing :: Typed",
    ],
)
