from setuptools import setup, find_packages

setup(
    name='urlshortener',
    version='1.0.0',
    packages=find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    description=('Basic in-memory URL shortener'),
    license='Apache 2',
)
