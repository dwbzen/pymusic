from setuptools import find_packages
from setuptools import setup
import os

ROOT_DIR = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(ROOT_DIR)

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

requirements = [
    'music21 >=10.5.0',
    'pandas >=3.0.3'
]

setup(
    name="dwbzen",
    version="1.0.0",
    author="Don Bacon",
    author_email="dwbzen@gmail.com",
    description="Music and Math package including MarkovChain generation from text and music source, and production",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dwbzen/dwbzen",
    packages=find_packages(exclude=["test",]),
    data_files=[('resources', ['resources/music/allChordFormulas.json','resources/music/clefs.json', 'resources/music/common_scaleFormulas.json',
                  'resources/music/instruments.json','resources/music/modern_Modes.json','resources/music/keys.json',
                  'resources/music/substitution_rules.json',
                  'resources/pos/2of12pos.txt', 'resources/pos/3eslpos.txt','resources/pos/5deskpos.txt',
                  'resources/text/drugBrandNames.txt'
                    ])],   
    install_requires=requirements,
    license="MIT",
    namespace_packages=[],
    include_package_data=False,
    classifiers=[
        "Development Status :: 3 - Alpha",
		"Intended Audience :: Developers",
        "Environment :: Console",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
	    "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
    ],
    python_requires='>=3.13',
    zip_safe=False,
    keywords="markov chain text music baseball",
    maintainer='Donald Bacon',
    maintainer_email='dwbzen@gmail.com'
)
