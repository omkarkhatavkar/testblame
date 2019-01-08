from setuptools import setup, find_packages


def get_requirements():
    with open("requirements.txt") as reqs_file:
        reqs = reqs_file.read().split("\n")
    return reqs

setup(
    name='TestBlame',
    version="0.1",
    description="collect the failed tests from junit report and send across report based on there commit history",
    author="Omkar Khatavkar",
    author_email="okhatavkar007@gmail.com",
    py_module=['testblame'],
    install_requires=get_requirements(),
    packages=find_packages("testblame"),
    entry_points={"console_scripts": ["testblame=testblame:cli"]},
)
