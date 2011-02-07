from setuptools import setup, find_packages
import commands

setup(
    name = "Mailgun",
    version = "0.2",
    packages = find_packages(),
    setup_requires = ['pyactiveresource',],
)

