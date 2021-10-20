from setuptools import find_packages
from setuptools import setup
import os

ROOT_DIR = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(ROOT_DIR)

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

requirements = [
    'music21 >=7.1.0',
    'pandas >=1.3.3'
]

setup(
    name="dwbzen",
    version="0.1.0",
    author="Don Bacon",
    author_email="dwbzen@gmail.com",
    description="Music and Math package including MarkovChain generation from text and music source, and production",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dwbzen/dwbzen",
    packages=find_packages(exclude=["test",]),
    install_requires=requirements,
    license="MIT",
    namespace_packages=[],
    include_package_data=False,
    zip_safe=False,
    classifiers=[
		"Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT",
        "Operating System :: OS Independent",
	    "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires='>=3.8',
    zip_safe=False,
    keywords="markov chain text music",
    maintainer='Donald Bacon',
    maintainer_email='dwbzen@gmail.com'
)
