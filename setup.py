from setuptools import setup, find_packages


version = '0.1-alpha'

install_requires = [
    "pygame",
]

setup(
    name='PyGauges',
    version=version,
    packages=find_packages(),
    url='http://rshk.github.io/PyGauges',
    license='Apache License, Version 2.0, January 2004',
    author='Samuele Santi',
    author_email='samuele@samuelesanti.com',
    description='',
    long_description='',
    install_requires=install_requires,
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Development Status :: 1 - Planning",
        "Programming Language :: Python :: 2.7",
    ],
    package_data={'': ['README.rst', 'LICENSE']})
