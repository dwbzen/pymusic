from setuptools import find_packages
from setuptools import setup
import os

ROOT_DIR = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(ROOT_DIR)

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

requirements = [
    'music21 >=7.1.0',
    'pandas >=1.4.3'
]

setup(
    name="dwbzen",
    version="0.2.0",
    author="Don Bacon",
    author_email="dwbzen@gmail.com",
    description="Music and Math package including MarkovChain generation from text and music source, and production",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dwbzen/dwbzen",
    packages=find_packages(exclude=["test",]),
    data_files=[('resources', ['resources/music/allChordFormulas.json','resources/music/clefs.json', 'resources/music/common_scaleFormulas.json',
                  'resources/music/commonScaleFormulas.json','resources/music/instruments.json','resources/music/keys.json','resources/music/substitution_rules.json',
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
	    "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires='>=3.10',
    zip_safe=False,
    keywords="markov chain text music baseball",
    maintainer='Donald Bacon',
    maintainer_email='dwbzen@gmail.com'
)
