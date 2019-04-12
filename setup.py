#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name='neonatal',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'tables<=3.4.0',
        'joblib>=0.13.0',
        'pandas<=0.23.4',
        'numpy<=1.15.4',
        'scipy',
        'xlrd',
        'drmaa',
        'billiard',
        'rq',
        'redis<=3.0.1',
        'vivarium-cluster-tools==1.0.7',
        'vivarium==0.8.18',
        'vivarium-gbd-access==2.0.2',
        'vivarium_public_health==0.9.10',
        'vivarium_inputs[data]==2.0.3',
        'gbd_mapping==2.0.3',
    ],
)
