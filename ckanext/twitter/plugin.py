import ckan.plugins as p
import ckanext.twitter.lib.config_helpers
from beaker.cache import cache_regions
from ckan.common import session
from ckanext.twitter.lib import config_helpers, helpers as twitter_helpers, cache_helpers


class TwitterPlugin(p.SingletonPlugin):
    '''
    Automatically send tweets when a dataset is updated or created.
    '''
    p.implements(p.IConfigurable, inherit=True)
    p.implements(p.IConfigurer)
    p.implements(p.IPackageController, inherit=True)
    p.implements(p.ITemplateHelpers, inherit=True)
    p.implements(p.IRoutes, inherit=True)

    # IConfigurable
    def configure(self, config):
        cache_regions.update({
            'twitter': {
                'expire':
                    ckanext.twitter.lib.config_helpers
                        .twitter_hours_between_tweets(),
                'type': 'memory',
                'enabled': True,
                'key_length': 250
                }
            })

    # IConfigurer
    def update_config(self, config):
        # Add templates
        p.toolkit.add_template_directory(config, 'theme/templates')
        # Add resources
        p.toolkit.add_resource('theme/fanstatic', 'ckanext-twitter')

    # IPackageController
    def after_update(self, context, pkg_dict):
        is_suitable = twitter_helpers.twitter_pkg_suitable(context,
                                                           pkg_dict['id'])
        if is_suitable:
            session.setdefault('twitter_is_suitable', pkg_dict['id'])
            session.save()

    # ITemplateHelpers
    def get_helpers(self):
        js_helpers = twitter_helpers.TwitterJSHelpers()
        return {
            'tweet_ready': js_helpers.tweet_ready,
            'get_tweet': js_helpers.get_tweet,
            'disable_edit': config_helpers.twitter_disable_edit
            }

    # IRoutes
    def before_map(self, _map):
        controller = 'ckanext.twitter.controllers.tweet:TweetController'
        _map.connect('post_tweet', '/dataset/{pkg_id}/tweet',
                     controller=controller, action='send',
                     conditions={
                         'method': ['POST']
                         })
        _map.connect('clear_tweet_cache', '/dataset/{pkg_id}/tweet-clear',
                     controller=controller, action='clear',
                     conditions={
                         'method': ['POST']
                         })
        return _map
