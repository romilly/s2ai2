from setuptools import setup, find_packages

setup(
    name="semantic_scholar",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0",
    ],
)