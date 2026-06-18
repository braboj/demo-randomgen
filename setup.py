from setuptools import setup, find_packages

VERSION = '0.0.2.0'
URL = 'https://github.com/braboj/randomgen'

LONG_DESCRIPTION = """
RandomGen is a project that provides an easy-to-use and easy-to-extend
framework for generating random data.

The web application runs as a web server and provides a RESTful API for
generating random data.
""".strip()

SHORT_DESCRIPTION = """
An application to generate random numbers using REST API.""".strip()

setup(
    name='randomgen',
    version=VERSION,
    url=URL,
    author='Branimir Georgiev',
    description=SHORT_DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(include=['randomgen', 'randomgen.*']),
    python_requires='>=3.12',
    install_requires=[
        'scipy~=1.14.1',
        'flask~=3.0.2',
        'gunicorn~=23.0',
    ],
)
