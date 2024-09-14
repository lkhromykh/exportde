from setuptools import setup, find_packages


def load_requirements():
    with open("requirements.txt", encoding="utf-8") as req:
        return req.readlines()


setup(
    name="exportde",
    packages=find_packages(),
    version="0.0.1",
    python_requires=">=3",
    install_requries=load_requirements()
)
