from setuptools import setup, find_packages


with open('README.md', 'r', encoding='utf-8') as handle:
    LONG_DESCRIPTION = handle.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='testblame',
    version="0.1",
    description="Collect the failed tests from junit report and send across report based on their"
                " commit history.",
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author="Omkar Khatavkar",
    author_email="okhatavkar007@gmail.com",
    url="https://github.com/omkarkhatavkar/testblame",
    py_modules=['testblame'],
    install_requires=required,
    packages=find_packages("testblame"),
    entry_points={"console_scripts": ["testblame=testblame:cli"]},
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
)
