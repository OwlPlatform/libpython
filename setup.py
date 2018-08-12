import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

setuptools.setup(
  name="libowl",
  version="0.0.1",
  author="Bernhard Firner",
  author_email="ben@owlplatform.com",
  description="Owl Platform implementation of the GRAIL protocol",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/OwlPlatform/libpython",
  packages=setuptools.find_packages(),
  classifiers=(
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    "Operating System :: OS Independent",
    ),
)
