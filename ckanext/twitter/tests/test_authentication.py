#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-twitter
# Created by the Natural History Museum in London, UK

import ckan.new_tests.helpers as helpers
import ckan.plugins as p
import ckanext.twitter.lib.config_helpers
import nose
from ckan.tests.pylons_controller import PylonsTestCase
from ckanext.twitter.lib import twitter_api
from ckanext.twitter.tests.helpers import Configurer

eq_ = nose.tools.eq_


class TestTwitterAuthentication(PylonsTestCase):
    @classmethod
    def setup_class(cls):
        super(TestTwitterAuthentication, cls).setup_class()
        cls.config = Configurer()
        if not p.plugin_loaded(u'twitter'):
            p.load(u'twitter')

    @classmethod
    def teardown_class(cls):
        cls.config.reset()
        p.unload(u'twitter')
        helpers.reset_db()

    def test_can_authenticate(self):
        ck, cs, tk, ts = ckanext.twitter.lib.config_helpers \
            .twitter_get_credentials()
        is_authenticated = twitter_api.twitter_authenticate()
        eq_(is_authenticated, True,
            u'Authentication not successful with key: {0} and secret: '
            u'{1}'.format(ck, cs))
