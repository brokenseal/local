# OPENSHIFT

from setuptools import setup

with open('requirements.txt', 'r') as requirements:
    # reuse already existing pip requirements file
    install_requires = [requirement.replace('\n', '') for requirement in requirements.readlines()]

    setup(name='YourAppName',
        version='1.0',
        description='OpenShift App',
        author='Your Name',
        author_email='example@example.com',
        url='http://www.python.org/sigs/distutils-sig/',
        install_requires=install_requires,
    )