from setuptools import setup, find_packages

with open('requirements.txt', 'r') as f:
    requirements = f.read().splitlines()

setup(
    name='Match-E',
    version='1.0.0',
    author='Match-E',
    author_email='info@match-e.com',
    description='Match-E',
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)
