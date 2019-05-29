#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name='stillbirth',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'tables<=3.4.0',
        'joblib>=0.13.0',
        'pandas',
        'numpy<=1.15.4',
        'scipy',
        'vivarium-cluster-tools>=1.0.9',
        'vivarium>=0.8.20',
        'vivarium_public_health>=0.9.12',
        'vivarium_inputs[data]>=2.0.3'
    ],
)
