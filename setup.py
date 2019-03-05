from setuptools import find_packages
from distutils.core import setup

DESC = 'Aiger <-> BDD bridge.'

setup(
    name='py-aiger-bdd',
    version='0.2.1',
    description=DESC,
    url='http://github.com/mvcisback/py-aiger-bdd',
    author='Marcell Vazquez-Chanlatte',
    author_email='marcell.vc@eecs.berkeley.edu',
    license='MIT',
    install_requires=[
        'py-aiger',
        'dd',
        'bidict',
        'parsimonious',
    ],
    packages=find_packages(),
)
