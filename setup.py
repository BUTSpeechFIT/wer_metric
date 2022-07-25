from setuptools import setup

setup(
    name='wer_metric',
    version='0.0.1',
    author="Martin Kocour",
    description="Word-error-rate computation",
    install_requires=[
        'numpy',
        'importlib-metadata; python_version == "3.7"',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
