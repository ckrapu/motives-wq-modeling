from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="mwqm",
    version="0.1.0",
    packages=["mwqm"],
    python_requires=">=3.8",
    install_requires=requirements,
)
