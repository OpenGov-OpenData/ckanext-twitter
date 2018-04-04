#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-twitter
# Created by the Natural History Museum in London, UK

from beaker.cache import cache_regions

import ckanext.twitter.lib.config_helpers
from ckan.common import session
from ckan.plugins import SingletonPlugin, implements, interfaces, toolkit
from ckanext.twitter.lib import config_helpers, helpers as twitter_helpers


class TwitterPlugin(SingletonPlugin):
    '''
    Automatically send tweets when a dataset is updated or created.
    '''
    implements(interfaces.IConfigurable, inherit=True)
    implements(interfaces.IConfigurer)
    implements(interfaces.IPackageController, inherit=True)
    implements(interfaces.ITemplateHelpers, inherit=True)
    implements(interfaces.IRoutes, inherit=True)

    # IConfigurable
    def configure(self, config):
        cache_regions.update({
            u'twitter': {
                u'expire':
                    ckanext.twitter.lib.config_helpers
                        .twitter_hours_between_tweets(),
                u'type': u'memory',
                u'enabled': True,
                u'key_length': 250
                }
            })

    # IConfigurer
    def update_config(self, config):
        # Add templates
        toolkit.add_template_directory(config, u'theme/templates')
        # Add resources
        toolkit.add_resource(u'theme/fanstatic', u'ckanext-twitter')

    # IPackageController
    def after_update(self, context, pkg_dict):
        is_suitable = twitter_helpers.twitter_pkg_suitable(context,
                                                           pkg_dict[u'id'])
        if is_suitable:
            session.setdefault(u'twitter_is_suitable', pkg_dict[u'id'])
            session.save()

    # ITemplateHelpers
    def get_helpers(self):
        js_helpers = twitter_helpers.TwitterJSHelpers()
        return {
            u'tweet_ready': js_helpers.tweet_ready,
            u'get_tweet': js_helpers.get_tweet,
            u'disable_edit': config_helpers.twitter_disable_edit
            }

    # IRoutes
    def before_map(self, _map):
        controller = u'ckanext.twitter.controllers.tweet:TweetController'
        _map.connect(u'post_tweet', '/dataset/{pkg_id}/tweet',
                     controller=controller, action=u'send',
                     conditions={
                         u'method': [u'POST']
                         })
        return _map
