from setuptools import setup,find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="jlpt-quiz-generator", # Changed for clarity
    version="0.1",
    author="Ritesh",
    packages=find_packages(),
    install_requires = requirements,
)