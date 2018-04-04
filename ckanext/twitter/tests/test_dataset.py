#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-twitter
# Created by the Natural History Museum in London, UK

import ckan.plugins as p
import nose
from ckan.tests.pylons_controller import PylonsTestCase
from ckanext.twitter.lib import (parsers as twitter_parsers)
from ckanext.twitter.tests.helpers import Configurer, DataFactory

eq_ = nose.tools.eq_


class TestDatasetMetadata(PylonsTestCase):
    @classmethod
    def setup_class(cls):
        super(TestDatasetMetadata, cls).setup_class()
        cls.config = Configurer()
        p.load(u'datastore')
        p.load(u'twitter')
        cls.df = DataFactory()

    @classmethod
    def teardown_class(cls):
        cls.config.reset()
        cls.df.destroy()
        p.unload(u'datastore')
        p.unload(u'twitter')

    def test_gets_dataset_author(self):
        pkg_dict = self.df.public_records
        eq_(pkg_dict[u'author'], u'Test Author',
            u'Author is actually: {0}'.format(
                    pkg_dict.get(u'author', u'no author set')))

    def test_gets_dataset_title(self):
        pkg_dict = self.df.public_records
        eq_(pkg_dict[u'title'], u'A test package',
            u'Title is actually: {0}'.format(
                    pkg_dict.get(u'title', u'no title set')))

    def test_gets_dataset_number_of_records_if_has_records(self):
        pkg_dict = self.df.public_records
        n_records = twitter_parsers.get_number_records(self.df.context,
                                                       pkg_dict[u'id'])
        eq_(n_records, 5,
            u'Calculated number of records: {0}\nActual number: 5'.format(
                    n_records))

    def test_gets_dataset_number_of_records_if_no_records(self):
        pkg_dict = self.df.public_no_records
        n_records = twitter_parsers.get_number_records(self.df.context,
                                                       pkg_dict[u'id'])
        eq_(n_records, 0,
            u'Calculated number of records: {0}\nActual number: 0'.format(
                    n_records))

    def test_gets_is_private(self):
        pkg_dict = self.df.public_records
        if pkg_dict.get(u'private', None) is None:
            access = u'unknown'
        elif pkg_dict.get(u'private', None):
            access = u'private'
        else:
            access = u'public'
        eq_(pkg_dict[u'private'], False,
            u'Package is actually: {0}'.format(access))
