#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-twitter
# Created by the Natural History Museum in London, UK

import nose

import ckanext.twitter.lib.config_helpers
from ckan import plugins
from ckan.tests import helpers
from ckanext.twitter.lib import twitter_api
from ckanext.twitter.tests.helpers import Configurer

eq_ = nose.tools.eq_


class TestTwitterAuthentication(helpers.FunctionalTestBase):
    @classmethod
    def setup_class(cls):
        super(TestTwitterAuthentication, cls).setup_class()
        cls.config = Configurer()
        if not plugins.plugin_loaded(u'twitter'):
            plugins.load(u'twitter')

    @classmethod
    def teardown_class(cls):
        cls.config.reset()
        plugins.unload(u'twitter')
        helpers.reset_db()

    def test_can_authenticate(self):
        ck, cs, tk, ts = ckanext.twitter.lib.config_helpers \
            .twitter_get_credentials()
        is_authenticated = twitter_api.twitter_authenticate()
        eq_(is_authenticated, True,
            u'Authentication not successful with key: {0} and secret: '
            u'{1}'.format(ck, cs))
