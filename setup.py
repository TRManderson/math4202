"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import sys

if not (sys.version_info.major == 3 and sys.version_info != 6):
    print("Requires Python 3.6")
    exit(1)

setup(
    name='ride_sharing',
    version='0.0.1',
    description='MATH4202: Stability in Ride Sharing',
    url='https://github.com/TRManderson/math4202-a1',
    author='Tom Manderson, Iain Rudge',
    author_email='me@trm.io, rudgeiain@gmail.com',
    classifiers=[
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(),
    install_requires=['attrs', 'click', 'gurobipy'],
    entry_points={
        'console_scripts': [
            'ride_sharing=ride_sharing.__main__:main',
        ],
    },
)
