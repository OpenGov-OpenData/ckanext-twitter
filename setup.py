#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-twitter
# Created by the Natural History Museum in London, UK

from setuptools import setup, find_packages

version = u'0.1'

setup(
    name=u'ckanext-twitter',
    version=version,
    description=u'Twitter DB updates',
    long_description=u'Sends a tweet every time a dataset is created or updated in the database.',
    classifiers=[],
    keywords=u'',
    author=[u'Alice Butcher'],
    author_email=u'data@nhm.ac.uk',
    url=u'https://github.com/NaturalHistoryMuseum/ckanext-twitter',
    license=u'',
    packages=find_packages(exclude=[u'ez_setup', u'list', u'tests']),
    namespace_packages=[u'ckanext', u'ckanext.twitter'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
    entry_points= \
        u'''
            [ckan.plugins]
            twitter=ckanext.twitter.plugin:TwitterPlugin
        ''',
)
