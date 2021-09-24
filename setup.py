import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dwbzen", # Replace with your own username
    version="0.0.1",
    author="Don Bacon",
    author_email="dwbzen@gmail.com",
    description="Music and Math package including MarkovChain generation from text and music source, and production",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dwbzen/dwbzen",
    packages=setuptools.find_packages(exclude=["test",]),
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
    keywords="markov chain text"
)